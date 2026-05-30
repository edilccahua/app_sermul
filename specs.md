# Especificación Técnica - SERMUL v3

**SERMUL** (Sistema de Gestión Logística y Control de Herramientas para Paradas de Planta) es un sistema diseñado para el control de inventario, trazabilidad de activos y equipos de protección personal (EPP) en entornos industriales.

## 1. Módulos del Sistema

El sistema se compone de los siguientes módulos funcionales:

*   **Módulo de Paradas:** Gestión del ciclo de vida de una campaña de mantenimiento (Planificada, Activa, Finalizada). Actúa como la entidad central que agrupa a los equipos de trabajo, tareas y movimientos históricos.
*   **Módulo de Catálogo e Inventario:** Control de unidades físicas mediante códigos cortos mnemotécnicos (*Short Codes*). El catálogo clasifica los ítems en: Herramientas Devolutivas, EPPs Devolutivos y Consumibles.
*   **Módulo de Operaciones (Pañol):** Interfaz para la asignación (Check-Out) y devolución (Check-In) de activos, gestionando los cambios de estado (Disponible, En Uso, Malograda, Perdida) y generando un historial auditable.
*   **Módulo de Reservas:** Funcionalidad de planificación pre-turno. Permite la creación, aprobación y posterior despacho unificado de listas de materiales.
*   **Módulo Offline:** Arquitectura PWA (Progressive Web App) que retiene en caché el inventario y encola transacciones de ventanilla localmente cuando no hay conectividad, sincronizándolas al recuperar la red.

## 2. Matriz de Roles (RBAC)

La seguridad y los flujos de autorización se basan en una jerarquía estricta:

| Nivel | Rol | Código | Responsabilidad Principal |
|-------|-----|--------|---------------------------|
| 1 | Residente | `RESIDENTE` | Gerencia operativa. Acceso a métricas financieras y autoridad exclusiva para el Cierre de Parada. |
| 1 | Administrador | `ADMIN` | Control técnico total sobre el sistema. |
| 2 | Supervisor Mecánico | `SUP_MEC` | Coordinación de grupos de trabajo y asignación de tareas. |
| 2 | Supervisor SSOMA | `SUP_SSOMA` | Auditoría de riesgos y procedimientos (rol observador). |
| 2 | Almacenero | `ALMACENERO` | Operador físico del almacén. Encargado de entregas, devoluciones y control de stock. |
| 3 | Líder Mecánico | `LIDER_MEC` | Encargado de cuadrilla. Autorizado para generar reservas de materiales pre-turno. |
| 4 | Trabajador | `TRABAJADOR` | Consulta de procedimientos y tareas asignadas. |

## 3. Máquina de Estados de Activos

Todas las herramientas y EPPs devolutivos siguen una transición de estados estricta en el `inventario_fisico`:

```text
[Disponible] ⇆ [En_Uso]
      ↓            ↓
 [Malograda]  [En_Mantenimiento] → [Disponible]
      ↓
 [Perdida] / [Baja] (Estados Terminales)
```

Todo cambio de estado genera un evento en la tabla `historial_movimientos` para garantizar la trazabilidad completa.

## 4. Requisitos No Funcionales Core

*   **Rendimiento Operativo:** Las operaciones de ventanilla deben concluirse en menos de 3 segundos por ítem para evitar interrupciones operativas.
*   **Resiliencia de Red:** Las funciones críticas de despacho deben estar disponibles en modo offline.
*   **Trazabilidad:** Cada transición de estado debe asociarse a un timestamp, un código de material, una parada activa y un registro auditable.

## 5. Decisiones Arquitectónicas y Actualizaciones Recientes

*   **Estandarización UI Fiori (Vistas Centrales):** Se ha garantizado la rigidez visual corporativa de Fiori alineando la arquitectura de componentes (`ParadasView`, `GruposView`, `PersonalView`, `AboutView`). Esto incluye el encapsulamiento de iconos principales (`w-7 h-7 flex items-center justify-center`), unificación de paddings de celdas (`px-3`) y eliminación estricta de bordes circulares web (`rounded-full` a `rounded-sm`).
*   **Enrutamiento Catch-All (404):** Se implementó una vista segura `NotFoundView.vue` anclada a la regla de enrutamiento `/:pathMatch(.*)*` para capturar accesos a URIs inexistentes sin colgar la PWA.
*   **Inyección de Credenciales (Hardcoded vs Seeds):**
    *   El usuario **Admin (12345678)** está acoplado permanentemente a la infraestructura base (`init.sql`) asegurando el acceso nativo, independiente de los flujos de pruebas.
    *   El usuario **Residente (11111111)** y el resto de personal (Almaceneros, Líderes) provienen exclusivamente del script de volumetría dinámica (`generate_seeds.py`), permitiendo flexibilidad extrema en simulaciones logísticas de alto impacto.
