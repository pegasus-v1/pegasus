# ══════════════════════════════════════════════════════════════════
# Pegasus API – Dockerfile (Desarrollo)
# ══════════════════════════════════════════════════════════════════
#
# Servicio:    Backend REST API
# Framework:   FastAPI + Uvicorn (ASGI)
# Base:        python:3.10-slim (Debian, ~45MB comprimido)
# Puerto:      8000
#
# ¿Cómo se usa?
#   - Se construye automáticamente con `docker compose up --build`
#   - También se puede construir manualmente:
#       docker build -t pegasus-api ./api
#       docker run -p 8000:8000 --env-file ./api/.env pegasus-api
#
# Estrategia de capas (caché):
#   1. Dependencias del sistema (gcc, libpq) → rara vez cambian
#   2. pip install requirements.txt          → cambian poco
#   3. Código fuente (COPY . .)             → cambia siempre
#   Al ordenarlas así, Docker reutiliza las capas 1-2 en cada build.
#
# ══════════════════════════════════════════════════════════════════

FROM python:3.10-slim

# ── Variables de entorno de Python ──────────────────────────────
# PYTHONDONTWRITEBYTECODE=1  → No genera archivos .pyc (innecesarios en contenedor)
# PYTHONUNBUFFERED=1         → Fuerza salida sin buffer (logs en tiempo real)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# ── Capa 1: Dependencias del sistema operativo ─────────────────
# gcc y libpq-dev son necesarios para compilar psycopg2-binary
# (driver de PostgreSQL). Se limpia la caché de apt para reducir
# el tamaño final de la imagen.
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# ── Capa 2: Dependencias de Python ─────────────────────────────
# Se copia SOLO requirements.txt primero. Si este archivo no cambia,
# Docker reutiliza la caché y no ejecuta pip install de nuevo.
# --no-cache-dir evita almacenar archivos temporales de pip.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Capa 3: Código fuente ──────────────────────────────────────
# Esta es la última capa porque el código cambia frecuentemente.
# NOTA: En desarrollo, docker-compose monta ./api:/app como volumen,
# así que esta capa solo se usa en builds standalone.
COPY . .

# Puerto expuesto (documentación, no abre el puerto realmente)
EXPOSE 8000

# ── Comando de arranque ────────────────────────────────────────
# Uvicorn arranca en modo desarrollo con --reload habilitado:
#   --host 0.0.0.0  → Acepta conexiones desde fuera del contenedor
#   --port 8000     → Puerto del servidor
#   --reload        → Reinicia automáticamente al detectar cambios en el código
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
