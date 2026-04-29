import asyncio
import logging
import random
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from langchain_huggingface import HuggingFaceEmbeddings
import psycopg2
import re
import string

MAX_RETRIES = 3

# ===============================
# LOGGING
# ===============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

# Configuración de embdedings
EMBEDDING_MODEL = "multilingual-e5-large" # Asegúrate de haber hecho 'ollama pull'

_model_instance = None

def get_embeddings_model():
    global _model_instance
    if _model_instance is None:
        print("📥 Cargando modelo E5 en memoria por primera vez (esto solo ocurre una vez)...")
        _model_instance = HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-large-instruct",
            model_kwargs={'device': 'cpu'}, # Usa 'cuda' si tienes GPU para ir 10x más rápido
            encode_kwargs={'normalize_embeddings': True},
            # Cache_folder evita que busque actualizaciones en internet cada vez
            cache_folder="./hf_model_cache" 
        )
    return _model_instance

# ===============================
# UTILIDADES
# ===============================
async def retry_with_backoff(coro_func, *args):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return await coro_func(*args)
        except Exception as e:
            if attempt == MAX_RETRIES:
                logger.error(f"Failed after {MAX_RETRIES} retries: {e}")
                return []
            wait_time = 2 ** attempt + random.uniform(0, 1)
            logger.warning(f"Retry {attempt} failed. Waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)

async def extract_feature_summary(browser, semaphore, producto,module_name, url):
    async with semaphore:
        page = await browser.new_page()
                
        logger.info(f"Processing Product: {producto} with Module: {module_name}")

        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_load_state("domcontentloaded")
            
            
            feature_summary_link = page.locator("a:has-text('Feature Summary')").first
            await feature_summary_link.click()

            await page.wait_for_selector("table", timeout=60000)

            tables = page.locator("table")
            table_count = await tables.count()

            for t in range(table_count):
                table = tables.nth(t)
                headers = table.locator("th")

                header_texts = [
                    (await headers.nth(i).inner_text()).strip()
                    for i in range(await headers.count())
                ]

                if (
                    "Feature" in header_texts
                    and any("Impact" in h for h in header_texts)
                    and any("Action" in h for h in header_texts)
                ):
                    rows = table.locator("tr")
                    row_count = await rows.count()

                    data = []
                    for r in range(1, row_count):
                        cols = rows.nth(r).locator("td")

                        if await cols.count() >= 3:
                            data.append({
                                "Module": module_name,
                                "Feature": (await cols.nth(0).inner_text()).strip(),
                                "Impact_to_Existing_Processes": (await cols.nth(1).inner_text()).strip(),
                                "Action_to_Enable": (await cols.nth(2).inner_text()).strip()
                            })

                    return data

        except PlaywrightTimeoutError:
            logger.warning(f"Timeout in {module_name}")
        except Exception as e:
            logger.error(f"Error in {module_name}: {e}")
        finally:
            await page.close()

        return []


async def extract_deprecated(browser, producto, url_template, version):
    page = await browser.new_page()
    
    
    data = []

    try:
        if "{version}" in url_template:
            target_url = url_template.format(version=version.lower())
        else:
            target_url = url_template

        logger.info(f"Investigando APIs en {producto}")

        await page.goto(target_url, timeout=60000)
        #await page.wait_for_selector("body")
        await page.wait_for_load_state("domcontentloaded")
    
        btn = page.locator("a:has-text('Deprecated REST Resources')").first

        if await btn.count() == 0:
            return []

        await btn.click()
        await page.wait_for_selector("table", timeout=60000)

        tables = page.locator("table")
        table_count = await tables.count()

        for t in range(table_count):
            table = tables.nth(t)
            headers = table.locator("th")

            header_texts = [
                (await headers.nth(i).inner_text()).strip()
                for i in range(await headers.count())
            ]

            if (
                "Deprecated Resource" in header_texts
                and any("Replacement Resource" in h for h in header_texts)
            ):

                rows = table.locator("tr")
                row_count = await rows.count()

                for r in range(1, row_count):
                    cols = rows.nth(r).locator("td")

                    if await cols.count() >= 3:
                        data.append({
                            "Module": producto,
                            "Deprecated_Resource": (await cols.nth(0).inner_text()).strip(),
                            "Replacement_Resource": (await cols.nth(1).inner_text()).strip(),
                            "Replacement_Resource_Paths": (await cols.nth(2).inner_text()).strip()
                        })

    except Exception as e:
        logger.error(f"Error en {producto}: {e}")

    finally:
        await page.close()

    return data



def get_embedding(texto: str, es_busqueda: bool = False):
    prefix = "query: " if es_busqueda else "passage: "
    return get_embeddings_model().embed_query(f"{prefix}{texto}")

def get_conn():
    return psycopg2.connect("postgresql://postgres:SalRam021@localhost:5432/vectordb")

def count_impacts(keywords, impactos_lista):
    return sum(1 for i in impactos_lista if any(k.lower() in i.Action_to_Enable.lower() for k in keywords))

def es_consulta_valida_oracle(texto: str) -> bool:
    # Lista de palabras clave obligatorias o versiones (24A, 25D, etc)
    import re
    patron_version = r"\b\d{2}[A-D]\b" # Busca 24A, 25B...
    keywords = ["oracle", "fusion", "erp", "cloud", "readiness", "impacto"]
    
    contenido = texto.lower()
    tiene_version = re.search(patron_version, contenido)
    tiene_keyword = any(k in contenido for k in keywords)
    
    return bool(tiene_version or tiene_keyword)

import re
import string

def normalizar_texto(texto: str) -> str:
    texto = texto.lower()
    texto = texto.replace("\n", " ")
    texto = texto.strip()
    # eliminar puntuación
    texto = texto.translate(str.maketrans("", "", string.punctuation))
    texto = re.sub(r"\s+", " ", texto)
    return texto

def detectar_ataque(texto: str) -> tuple[bool, str]:
    """
    Devuelve (es_ataque: bool, motivo: str).
    Comprueba tanto el texto original en minúsculas como la versión normalizada.
    """
    if not texto:
        return False, ""

    texto_raw = texto.lower()
    texto_norm = normalizar_texto(texto)

    # patrones
    raw_sql_patterns = [
        r";",
        r"--",
        r"/\*",
    ]

    # patrones basados en palabras clave
    keyword_patterns = [
        r"\bselect\b\s+.*\bfrom\b",
        r"\binsert\b\s+into\b",
        r"\bdelete\b\s+from\b",
        r"\bupdate\b\s+\w+\s+set\b",
        r"\bcreate\b\s+table\b",
        r"\balter\b\s+table\b",
        r"\bdrop\b\s+table\b",
        r"\btruncate\b\s+table\b",
        r"\bunion\b\s+select\b",
        r"\bexec\b\s*\(",
        r"\bexecute\b\s*\(",
        r"\bshow\b\s+tables\b",
        r"\bdescribe\b\s+\w+\b",
    ]

    # Primero revisar raw patterns
    for pattern in raw_sql_patterns:
        if re.search(pattern, texto_raw, re.IGNORECASE):
            return True, "Consulta SQL detectada (caracteres SQL en texto crudo)"

    # Luego revisar keywords sobre texto raw y normalizado
    for pattern in keyword_patterns:
        if re.search(pattern, texto_raw, re.IGNORECASE) or re.search(pattern, texto_norm, re.IGNORECASE):
            return True, "Consulta SQL detectada (patrón de palabras clave)"

    # patrones de prompt injection
    prompt_injection_patterns = [
        r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
        r"forget\s+(everything|all|your\s+instructions)",
        r"(new|different)\s+(role|persona|identity|instructions)",
        r"act\s+as\s+(if\s+you\s+are|a\s+different)",
        r"pretend\s+(you\s+are|to\s+be)",
        r"override\s+(your\s+)?(instructions|behavior|rules)",
        r"disregard\s+(the\s+)?(above|previous|system)",
        r"you\s+are\s+now\s+a",
        r"system\s*:\s*",
        r"<\s*system\s*>",
        r"jailbreak",
        r"do\s+anything\s+now",
        r"dan\s+mode",
        r"system prompt",
        r"assistant prompt",
        r"user prompt",
    ]

    for pattern in prompt_injection_patterns:
        if re.search(pattern, texto_raw, re.IGNORECASE) or re.search(pattern, texto_norm, re.IGNORECASE):
            return True, "Intento de modificar el comportamiento del agente detectado"

    return False, ""