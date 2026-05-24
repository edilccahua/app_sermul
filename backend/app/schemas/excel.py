from pydantic import BaseModel


class ExcelImportFilaError(BaseModel):
    fila: int
    dni: str
    error: str


class ExcelImportFilaWarning(BaseModel):
    fila: int
    dni: str
    warning: str


class ExcelImportResumen(BaseModel):
    filas_procesadas: int
    grupos_creados: int
    grupos_actualizados: int
    usuarios_creados: int
    usuarios_actualizados: int
    integrantes_agregados: int
    errores: int
    warnings: int


class ExcelImportResponse(BaseModel):
    resumen: ExcelImportResumen
    errores: list[ExcelImportFilaError] = []
    warnings: list[ExcelImportFilaWarning] = []
    grupos_creados_detalle: list[dict] = []
