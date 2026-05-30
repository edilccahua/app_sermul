#!/bin/bash
# ============================================================
# SERMUL - Script de Copia de Seguridad de la Base de Datos
# ============================================================

set -e

# Directorio de backups
BACKUP_DIR="$(dirname "$0")/../backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/sermul_db_backup_${TIMESTAMP}.sql"

# Crear directorio de backups si no existe
mkdir -p "${BACKUP_DIR}"

echo "Iniciando copia de seguridad de la base de datos sermul_db..."

# Obtener credenciales desde .env en la raíz
ENV_FILE="$(dirname "$0")/../.env"
if [ -f "$ENV_FILE" ]; then
    # Cargar variables de entorno
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

DB_USER=${POSTGRES_USER:-sermul_user}
DB_NAME=${POSTGRES_DB:-sermul_db}

# Ejecutar pg_dump dentro del contenedor db y volcar a local
docker compose exec -T db pg_dump -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE"

echo "Copia de seguridad completada con éxito."
echo "Archivo guardado en: $BACKUP_FILE"

# Comprimir backup
gzip "$BACKUP_FILE"
echo "Archivo comprimido: ${BACKUP_FILE}.gz"

# Mantener solo los últimos 7 días de copias (rotación)
find "$BACKUP_DIR" -name "sermul_db_backup_*.sql.gz" -mtime +7 -exec rm {} \;
echo "Rotación de backups completada (se mantienen los últimos 7 días)."
