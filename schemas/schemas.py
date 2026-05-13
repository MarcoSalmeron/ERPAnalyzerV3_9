from pydantic import BaseModel, Field
from typing import List

class FasePlan(BaseModel):
    fase: str; periodo: str; actividades: str; responsable: str

class ItemSoporte(BaseModel):
    servicio: str; descripcion: str
    
class Impacto(BaseModel):
    Module: str = Field(description="Nombre del módulo de Oracle Cloud")
    Feature: str = Field(description="Nombre de la funcionalidad o cambio")
    Impact_to_Existing_Processes: str = Field(
        alias="Impact_to_Existing_Processes",
        description="Descripción del impacto en procesos existentes"
    )
    Action_to_Enable: str = Field(
        alias="Action_to_Enable",
        description="Acción requerida para habilitar la funcionalidad"
    )


class ApiDeprecada(BaseModel):
    Module: str = Field(description="Producto o módulo Oracle")
    Deprecated_Resource: str = Field(
        alias="Deprecated_Resource",
        description="Recurso REST que fue deprecado"
    )
    Replacement_Resource: str = Field(
        alias="Replacement_Resource",
        description="Recurso REST que reemplaza al anterior"
    )
    Replacement_Resource_Paths: str = Field(
        alias="Replacement_Resource_Paths",
        description="Ruta del nuevo recurso REST"
    )


class   ReporteInvestigacion(BaseModel):
    impactos: List[Impacto] = Field(
        description="Lista de impactos funcionales detectados en la versión"
    )
    apis_deprecadas: List[ApiDeprecada] = Field(
        description="Lista de APIs REST marcadas como deprecadas"
    )
    plan_accion: List[FasePlan]
    proximos_pasos: List[str]
    servicios_soporte: List[ItemSoporte]

class ERPState(BaseModel):
    erp_module: str | None = None

class GoogleTokenRequest(BaseModel):
    credential: str