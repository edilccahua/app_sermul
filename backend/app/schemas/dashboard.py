from pydantic import BaseModel

from .parada import ParadaResponse


class PerdidasParadaResumen(BaseModel):
    parada_id: int
    codigo_parada: str
    nombre_parada: str
    total_perdido: float
    cantidad_perdidas: int


class GrupoHerramientasResumen(BaseModel):
    grupo_id: int
    codigo_grupo: str
    nombre_grupo: str
    herramientas_en_uso: int


class DashboardResidenteResponse(BaseModel):
    # Saturación
    pct_herramientas_en_uso: float
    herramientas_disponibles: int
    herramientas_en_uso: int
    herramientas_malogradas: int
    herramientas_perdidas: int

    # Valor monetario
    costo_total_perdidas: float
    costo_total_inventario: float

    # Gráficos
    perdidas_por_parada: list[PerdidasParadaResumen] = []
    top_grupos_herramientas: list[GrupoHerramientasResumen] = []
    herramientas_mas_usadas: list[dict] = []

    # Alertas
    paradas_activas: list[ParadaResponse] = []
    pendientes_cierre: int = 0
    reservas_pendientes: int = 0
    epps_por_vencer: int = 0
