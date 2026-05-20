# ============================================
# SERMUL Frontend - PRODUCCIÓN
# Multi-stage: Node 20 (build) → Nginx (serve)
# ============================================

# --- Etapa 1: Build ---
FROM node:20-alpine AS build

WORKDIR /app

# Instalar dependencias primero (cache de capas)
# Usa npm ci si existe package-lock.json (builds reproducibles),
# de lo contrario npm install para generarlo
COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copiar código fuente y construir
COPY . .
RUN npm run build

# --- Etapa 2: Servir con Nginx ---
FROM nginx:1.25-alpine

# Copiar configuración personalizada de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar los archivos construidos al directorio de Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Puerto expuesto (docker-compose.yml: "80:80")
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
