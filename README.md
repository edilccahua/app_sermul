<div align="center">
  <h1>⚙️ SERMUL</h1>
  <p><b>Sistema de Gestión Logística y Control de Herramientas para Paradas de Planta</b></p>
  
  <p>
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
    <img src="https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vue.js&logoColor=4FC08D" alt="Vue.js" />
    <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS" />
    <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  </p>
</div>

## 📖 Descripción General

**LOGIST v0.9 (Beta)** (Sistema de Requerimientos y Movimientos Logísticos) es una plataforma integral diseñada específicamente para optimizar el control de activos, herramientas y equipos de protección personal (EPP) durante las **Paradas de Planta** en el sector minero e industrial. 

El sistema digitaliza el flujo completo de almacén, desde la planificación pre-parada hasta la liquidación final, asegurando trazabilidad absoluta de cada activo, reduciendo los tiempos de atención en ventanilla y mitigando las pérdidas económicas por extravíos no documentados.

> [!NOTE]
> Para una descripción técnica profunda, los modelos de base de datos y la arquitectura detallada, revisa la **[Especificación Técnica de SERMUL (specs.md)](file:///home/edilsonc/Documents/SERMUL%20APP/app_sermul/specs.md)**.

---

## 🛠️ Stack Tecnológico

El proyecto está construido bajo una arquitectura moderna y escalable, dividida funcionalmente en backend y frontend, orquestados mediante contenedores.

### Backend (API RESTful)
- **Framework:** FastAPI (Python 3.11+) para alta concurrencia y validación estricta de datos (Pydantic).
- **ORM & Base de Datos:** SQLAlchemy 2.0 y PostgreSQL 15.
- **Seguridad:** Autenticación JWT con encriptación `bcrypt` y control de acceso basado en roles (RBAC).

### Frontend (SPA & PWA)
- **Core:** Vue 3 (Composition API) y Vite.
- **Estado Global:** Pinia.
- **Estilos y UI:** Tailwind CSS con componentes headless (`shadcn-vue`), adaptado estrictamente a los lineamientos de **SAP Fiori**.

### Infraestructura y Despliegue
- **Contenedores:** Docker y Docker Compose.
- **Servidor Web / Proxy:** Nginx (para entornos productivos).

---

## 🏭 Contexto Operativo y Flujo de Negocio

### El Problema (Entorno de Gran Minería)
Durante una parada de planta (mantenimiento mayor), intervienen cientos de técnicos divididos en cuadrillas de trabajo. En las primeras horas del turno, se genera un "cuello de botella" masivo en las ventanillas de los pañoles (almacenes). 
La presión por despachar rápidamente provoca registros manuales deficientes, lo que imposibilita el seguimiento. Al final de la parada, decenas de herramientas de alto costo (tecles, torquímetros, taladros) se reportan como perdidas sin un responsable claro.

### Solución SERMUL (Flujo Operativo)

1. **Gestión de Cuadrillas (Grupos de Trabajo):** 
   El sistema permite estructurar al personal en grupos (8-12 técnicos) liderados por un "Líder Mecánico" y supervisados por un "Supervisor SSOMA" o "Supervisor Mecánico". Cada grupo se asigna a un área específica (Ej: *Circuito de Molienda*).
2. **Dinámica de Ventanilla (Check-in / Check-out):**
   - **Despacho ultrarrápido:** El almacenero utiliza "Short Codes" mnemotécnicos (ej. `TALNEUM-ATLA` para un taladro neumático) para despachar. 
   - **Responsabilidad Directa:** Toda herramienta despachada queda anclada al ID del usuario que la retira y al código de su cuadrilla.
   - **Reservas Pre-turno:** Los líderes pueden realizar requerimientos de herramientas el día anterior. En ventanilla, el almacenero solo aprueba la reserva y entrega el bloque completo en segundos.
3. **Seguimiento y Trazabilidad (Auditoría):**
   Cada movimiento genera un registro inmutable en el historial. El sistema rastrea el ciclo de vida de un activo: `Disponible → En Uso → Malograda / Pérdida`. Las liquidaciones de parada permiten generar reportes de descuentos al personal por activos no devueltos.

---

## 🎨 Sistema de Diseño (SAP Fiori)

Para garantizar un entorno familiar en el sector corporativo-minero y asegurar la máxima legibilidad en condiciones industriales (iluminación variable, pantallas industriales), SERMUL implementa una adaptación estricta de **SAP Fiori (Morning Horizon)** utilizando **Tailwind CSS**.

- **Variables Inmutables:** No se utilizan colores arbitrarios. Todo color, borde o fondo está atado a tokens semánticos (ej. `var(--sapBackgroundColor)`, `var(--sapButton_Emphasized_Background)`).
- **Geometría Industrial:** Se erradicaron los bordes excesivamente redondeados de la web moderna en favor de componentes compactos (`radius: 2px`) para maximizar la densidad de datos en tablas y formularios.
- **Taxonomía de Estados (Indicators):** El estado del inventario utiliza paletas semánticas estrictas:
  - 🟢 **Success:** Herramientas devueltas / Disponibles.
  - 🔵 **Information:** Herramientas en uso (asignadas).
  - 🟡 **Warning:** En mantenimiento / Tránsito.
  - 🔴 **Error:** Herramientas malogradas o perdidas.

---

## 📂 Estructura de Directorios

```text
app_sermul/
├── docker-compose.yml       # Orquestación de servicios (Base de datos, Backend, Frontend)
├── README.md                # Documentación del proyecto
├── specs/                   # Especificaciones técnicas y requerimientos formales del sistema
├── backend/
│   ├── app/                 # Código fuente FastAPI
│   │   ├── api/             # Controladores y endpoints REST
│   │   ├── core/            # Configuración, seguridad (JWT) y manejo de errores
│   │   ├── models/          # Modelos de base de datos SQLAlchemy
│   │   ├── schemas/         # Validadores Pydantic (Request/Response)
│   │   └── services/        # Lógica de negocio encapsulada
│   ├── sql/                 # Scripts SQL base y generadores de mock-data
│   └── tests/               # Pruebas unitarias y de integración (Pytest)
└── frontend/
    ├── src/
    │   ├── api/             # Interceptores Axios y clientes de los endpoints
    │   ├── assets/          # Íconos de SAP (sap-icons), fuentes y estilos base globales
    │   ├── components/      # Componentes UI reutilizables (Botones, Modales, Badges)
    │   ├── stores/          # Estado global (Pinia: Auth, UI state)
    │   └── views/           # Páginas principales del sistema (Dashboards, Módulos)
    └── memory/rules/        # Documentación de lineamientos de diseño (Frontend Guidelines)
```

---

## 🚀 Guía de Instalación y Entorno Local

SERMUL está preparado para ser ejecutado rápidamente en entornos aislados usando Docker, pero también soporta despliegues nativos para un desarrollo granular.

### Despliegue con Docker

Requisitos: `Docker 24+` y `Docker Compose 2.23+`.

1. Clona el repositorio y configura el entorno:
   ```bash
   git clone https://github.com/edilccahua/app_sermul.git
   cd app_sermul
   cp .env.example .env  # Ajusta las contraseñas y secrets en este archivo
   ```
2. Levanta la infraestructura completa (construirá las imágenes e inicializará PostgreSQL):
   ```bash
   docker compose up -d --build
   ```
3. Verifica los servicios:
   - Frontend: [http://localhost](http://localhost) (o `http://localhost:5173` en desarrollo)
   - Backend Docs (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)

**Credenciales de Prueba:**
Todos los usuarios generados usan su **DNI como contraseña**. Ejemplos:
- **Admin (Sistema):** `12345678` *(Inyectado por defecto desde la inicialización de la BD) y/o Generado vía seeds*

### Entorno de Producción o Customizado
Si deseas iniciar tu propio entorno sin los cientos de registros falsos generados para pruebas, hemos proporcionado un archivo de plantilla básico y genérico llamado `seeds_example.sql`.

Este archivo contiene la estructura mínima requerida para crear categorías iniciales, un par de herramientas de ejemplo, y tus usuarios base.

```bash
# Inyectar tu propia data basándote en la plantilla
docker compose exec -T db psql -U user -d db < backend/sql/seeds_example.sql
```
> **Tip:** Copia el archivo `seeds_example.sql`, modifica los DNI y Catálogo según las necesidades de tu empresa, y ejecútalo para tener un inicio limpio.

---

## 🔧 Mantenimiento y Calidad de Código

```bash
# Ver logs en tiempo real del backend
docker compose logs -f backend

# Correr pruebas unitarias de backend
docker compose exec backend pytest

# Ejecutar linters de código (Python)
docker compose exec backend ruff check backend/
docker compose exec backend mypy backend/

# Ejecutar linters (Vue/JavaScript)
docker compose exec frontend npm run lint
```