# SERMUL

Sistema de Gestión Logística y Control de Herramientas para Paradas de Planta en Gran Minería.

## Problema

Durante las paradas de planta se manejan cientos de herramientas y activos especializados entre múltiples grupos de trabajo en un entorno hostil. La falta de control genera pérdidas económicas por extravío, demoras en ventanilla y ausencia de trazabilidad sobre responsables.

## Objetivo

Proveer control en tiempo real de herramientas, responsables y costos. Reducir el tiempo de entrega en ventanilla a menos de 1 minuto por transacción usando códigos cortos (short codes), eliminar pérdidas no documentadas y generar reportes ejecutivos de trazabilidad.

## Alcance

- Gestión de herramientas devolutivas con short codes mnemotécnicos (ej: HER-001)
- Check-in / check-out con confirmación visual y sonora
- Historial de movimientos con trazabilidad por parada
- Sistema de reservas pre-turno
- Gestión del ciclo de vida de paradas (Planificada > Activa > Finalizada)
- Cierre formal de parada con reporte de perdidas
- Grupos de trabajo con carga masiva por Excel
- Biblioteca de PETARs informativos
- Clasificacion de trabajos de riesgo
- Modo offline con sincronizacion automatica (PWA)
- Dashboards ejecutivos con costos y responsables
- Control de EPPs devolutivos con certificación y vida útil
- Consumibles con alertas de stock mínimo

## Stack tecnologico

| Capa | Tecnologia |
|------|-----------|
| Backend | FastAPI (Python 3.11+), SQLAlchemy 2.0 |
| Base de datos | PostgreSQL 15 |
| Frontend | Vue 3 (Composition API), Tailwind CSS, shadcn-vue |
| State | Pinia |
| Offline | Dexie.js (IndexedDB), Workbox (Service Workers) |
| Autenticacion | JWT (python-jose + passlib[bcrypt]) |
| Infraestructura | Docker Compose |

## Estructura

```
app_sermul/
├── docker-compose.yml
├── backend/
│   ├── app/                  # FastAPI: models, schemas, api, services, core
│   ├── sql/init.sql          # DDL completo
│   └── tests/
├── frontend/
│   └── src/                  # Vue 3: components, views, stores, router
```

## Ejecucion

### Requisitos

- Docker 24+ y Docker Compose 2.23+ (opcional, ver "Sin Docker")
- PostgreSQL 15 corriendo localmente o accesible en red
- Python 3.11+
- Node.js 18+
- 4 GB RAM disponible

### Clonar y levantar

```bash
git clone https://github.com/edilccahua/app_sermul.git
cd app_sermul

# Configurar variables de entorno (Base de datos y Backend JWT)
cp .env.example .env # Edita .env con tus credenciales

# Levantar los servicios
docker compose up -d --build
```

### Sin Docker (desarrollo local desde ZIP)

Si no usas Docker o prefieres desarrollar localmente:

```bash
# 1. PostgreSQL — crear la base de datos
createdb sermul
psql -d sermul -f backend/sql/init.sql

# 2. Backend
cd backend
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
cp .env.example .env            # Editar DATABASE_URL y SECRET_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload   # http://localhost:8000

# 3. Frontend (otra terminal)
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

**Nota:** El proxy de Vite (`vite.config.js`) redirige `/api` a `http://localhost:8000`. Asegúrate de que el backend esté corriendo antes de usar el frontend.

### Desarrollo Local de Backend

Para desarrollar localmente, puedes crear un entorno virtual local:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Verificar

```bash
docker compose ps
curl http://localhost:8000/api/health
curl http://localhost:8000/docs
curl http://localhost:80
```

### Credenciales de prueba

| DNI | Usuario | Rol | Password |
|-----|---------|-----|----------|
| 12345678 | Carlos Rodriguez | Residente | admin123 |
| 87654321 | Sistema Admin | Administrador | admin123 |
| 11223344 | Juan Perez | Almacenero | almacen123 |

### Comandos utiles

```bash
docker compose logs -f backend              
docker compose exec backend pytest          # Tests
docker compose exec frontend npm run lint   # Lint
docker compose restart backend              # Reiniciar un servicio
docker compose down -v                      # Bajar todo y borrar datos
```

## Documentación

Para conocer los detalles arquitectónicos, la lógica de negocio y las reglas del sistema, consulte la especificación técnica formal:

* [Especificación Técnica (specs.md)](./specs.md)