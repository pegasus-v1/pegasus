# ══════════════════════════════════════════════════════════════════
# Pegasus Web – Dockerfile (Desarrollo)
# ══════════════════════════════════════════════════════════════════
#
# Servicio:    Dashboard Frontend
# Framework:   React 18 (Create React App)
# Base:        node:18-alpine (Alpine Linux, ~40MB comprimido)
# Puerto:      3000
#
# ¿Cómo se usa?
#   - Se construye automáticamente con `docker compose up --build`
#   - También se puede construir manualmente:
#       docker build -t pegasus-web ./web
#       docker run -p 3000:3000 pegasus-web
#
# Estrategia de capas (caché):
#   1. package.json + package-lock.json  → npm install se cachea
#   2. Código fuente (COPY . .)          → cambia frecuentemente
#   Esto evita reinstalar node_modules en cada cambio de código.
#
# Comunicación con el backend:
#   - El proxy de CRA está configurado en package.json como
#     "proxy": "http://api:8000", donde "api" es el nombre del
#     servicio definido en docker-compose.yml.
#   - Dentro de la red Docker, los servicios se comunican por
#     nombre de servicio (DNS interno de Docker).
#
# ══════════════════════════════════════════════════════════════════

FROM node:18-alpine

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# ── Capa 1: Dependencias de Node.js ────────────────────────────
# Se copian SOLO los manifiestos de dependencias primero.
# El asterisco en package-lock.json* evita error si no existe.
# --legacy-peer-deps previene fallos por conflictos de peer deps
# en versiones más recientes de npm.
# Si package.json NO cambia → Docker reutiliza esta capa completa
# y no ejecuta npm install de nuevo (ahorra ~30-60 segundos).
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps

# ── Capa 2: Código fuente ──────────────────────────────────────
# Se copia el resto del código (src/, public/, etc.)
# NOTA: En desarrollo, docker-compose monta ./web:/app como volumen,
# y un volumen anónimo protege /app/node_modules para que los
# módulos instalados en el contenedor no se sobrescriban.
COPY . .

# Puerto expuesto (CRA dev server por defecto usa 3000)
EXPOSE 3000

# ── Comando de arranque ────────────────────────────────────────
# `npm start` ejecuta `react-scripts start`, que:
#   - Levanta el servidor de desarrollo en el puerto 3000
#   - Habilita Hot Module Replacement (HMR) para ver cambios al instante
#   - Usa el proxy definido en package.json para redirigir llamadas /api/*
CMD ["npm", "start"]
