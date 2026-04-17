import os
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.units import inch
from pathlib import Path

# --- CONFIGURACIÓN DE COLORES CORPORATIVOS ---
AZUL_CONDOR = colors.HexColor("#004A99")
ROJO_ORACLE = colors.HexColor("#FF0000")
GRIS_FILA = colors.HexColor("#F2F2F2")
GRIS_TEXTO = colors.HexColor("#4D4D4D")

class ReporteCorporativo(SimpleDocTemplate):
    def __init__(self, filename, version, **kwargs):
        super().__init__(filename, **kwargs)
        self.version = version
        # Ruta absoluta robusta
        base_path = Path(__file__).parent.parent
        self.logo_path = str(base_path / "assets" / "logo_condor.png")
        print(f"DEBUG: Buscando logo en: {self.logo_path}") 

    def afterFlowable(self, flowable):
        self.canv.saveState()
        
            
        # 1. DIBUJAR FONDO AZUL (Base)
        #self.canv.setFillColor(AZUL_CONDOR)
        # Stroke=0 es vital para que no haya bordes negros tapando el logo
        #self.canv.rect(0.5*inch, 10.1*inch, 2.2*inch, 0.6*inch, fill=1, stroke=0)
        
        # 3. PÍLDORA ROJA ORACLE
        self.canv.setFillColor(ROJO_ORACLE)
        self.canv.roundRect(6.5*inch, 10.25*inch, 1.5*inch, 0.35*inch, 0.15*inch, fill=1, stroke=0)
        self.canv.setFillColor(colors.white)
        self.canv.setFont("Helvetica-Bold", 10)
        self.canv.drawCentredString(7.25*inch, 10.35*inch, "ORACLE Partner")

        # 4. PORTADA (Solo Pág 1)
        pagina_actual = self.canv.getPageNumber()
        if pagina_actual == 1:
           
            
            AZUL_CLARO = colors.HexColor("#F0F7FF")
            self.canv.setFillColor(AZUL_CLARO)
            self.canv.roundRect(0.5*inch, 8.2*inch, 7.5*inch, 1.2*inch, 0.1*inch, fill=1, stroke=0)
            self.canv.setFillColor(GRIS_TEXTO)
            self.canv.setFont("Helvetica-Bold", 10)
            self.canv.drawString(0.7*inch, 9.1*inch, "Elaborado por:")
            
            self.canv.setFillColor(AZUL_CONDOR)
            self.canv.setFont("Helvetica-Bold", 16)
            self.canv.drawString(0.7*inch, 8.8*inch, "INGENIERÍA CONDOR ")
            
            self.canv.setFillColor(colors.HexColor("#4472C4"))
            self.canv.setFont("Helvetica", 10)
            self.canv.drawString(0.7*inch, 8.65*inch, "Oracle Cloud Managed Service Specialist")
            
            self.canv.setFillColor(GRIS_TEXTO)
            self.canv.setFont("Helvetica", 8)
            contact_info = "contacto@i-condor.com | www.i-condor.com | +52 (55) 2563 5292"
            self.canv.drawString(0.7*inch, 8.4*inch, contact_info)
            self.canv.drawString(0.7*inch, 8.25*inch, "Marzo 2026")
            if os.path.exists(self.logo_path):
                try:
                                      
                    self.canv.drawInlineImage(
                        self.logo_path,
                        0.7*inch,            # misma X que el texto
                        8.25*inch - 0.85*inch,  # ajusta este valor según el alto de la imagen
                        width=1*inch,
                        height=0.8*inch,
                        preserveAspectRatio=True
                    )
                except Exception as e:
                    # Si la imagen falla, ponemos el nombre para no dejarlo vacío
                    self.canv.setFillColor(AZUL_CONDOR)
                    self.canv.setFont("Helvetica-Bold", 12)
                    self.canv.drawCentredString(1.65*inch, 10.35*inch, "CONDOR")
                    print(f"DEBUG: Fallo en imagen: {e}")
        
            
        self.canv.restoreState()
