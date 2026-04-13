#  Pegasus - Quick Start Guide

Bienvenido al proyecto **Pegasus**. Esta guía te ayudará a poner en marcha tanto la API como la Web usando Docker Compose en pocos minutos.

##  Requisitos Previos

Asegúrate de tener instalado:
- **Docker** (versión 20.10 o superior)
- **Docker Compose** (versión 2.0 o superior)
- **Git** (opcional, para clonar el repositorio)

> **Nota**: Si no tienes Docker instalado, descárgalo desde [docker.com](https://www.docker.com/get-started).

---

##  1. Obtener el Proyecto

1. **Clona el repositorio** (o descomprime si ya lo tienes):
   ```bash
   git clone <url-del-repositorio>
   cd pegasus
   ```

2. **Verifica que estés en la carpeta raíz** del proyecto:
   ```bash
   ls -la
   ```
   Deberías ver archivos como `docker-compose.yml`, `api/`, `web/`, etc.

---

##  2. Levantar los Servicios con Docker Compose

Docker Compose orquestará automáticamente la API (FastAPI) y la Web (React).

1. **Asegúrate de que Docker esté corriendo**:
   - Abre Docker Desktop o verifica con:
     ```bash
     docker info
     ```

2. **Construye y levanta los contenedores**:
   ```bash
   docker compose up --build
   ```
   > Este comando:
   > - Descarga las imágenes base (Python 3.10 y Node.js 18)
   > - Construye las imágenes personalizadas para API y Web
   > - Crea y inicia los contenedores
   > - Monta los volúmenes para desarrollo (hot-reload)

3. **Espera a que termine la construcción**:
   - La primera vez tomará varios minutos (descarga de imágenes y instalación de dependencias).
   - Verás logs como:
     ```
     [+] Building 2/2
     ✔ Container pegasus-api  Built
     ✔ Container pegasus-web  Built
     Attaching to pegasus-api, pegasus-web
     pegasus-api  | INFO:     Will watch for changes...
     pegasus-web  | Compiled successfully!
     ```

4. **Verifica que los servicios estén corriendo**:
   ```bash
   docker compose ps
   ```
   Deberías ver:
   ```
   NAME               IMAGE     COMMAND                  SERVICE   CREATED         STATUS          PORTS
   pegasus-api        pegasus-api   "uvicorn main:app --hos…"   api       2 minutes ago   Up 2 minutes    0.0.0.0:8000->8000/tcp
   pegasus-web        pegasus-web   "npm start"                 web       2 minutes ago   Up 2 minutes    0.0.0.0:3000->3000/tcp
   ```

---

##  3. Acceder a la Aplicación

Una vez que los contenedores estén corriendo:

1. **Abre tu navegador** y ve a:
   - **Dashboard Web**: http://localhost:3000
   - **API Docs (Swagger)**: http://localhost:8000/docs
   - **API Redoc**: http://localhost:8000/redoc
   - **Health Check**: http://localhost:8000/health

2. **Prueba la funcionalidad**:
   - En el dashboard, selecciona una fecha y un clan.
   - Haz click en los botones "Asistieron", "Tarde", etc.
   - Usa el buscador para encontrar estudiantes.

---

##  4. Detener y Limpiar

Cuando termines:

1. **Detén los contenedores** (presiona `Ctrl+C` en la terminal donde corre `docker compose up`).

2. **Opcional: Elimina contenedores y volúmenes**:
   ```bash
   docker compose down -v
   ```

3. **Para desarrollo continuo**:
   ```bash
   docker compose up --build -d
   ```
   > El flag `-d` corre en background. Usa `docker compose logs -f` para ver logs.

---

## 🔧 Solución de Problemas

### El comando `docker compose up --build` no hace nada
- Verifica que Docker esté corriendo: `docker info`
- Asegúrate de estar en la carpeta correcta: `pwd`
- Intenta `docker compose build` primero, luego `docker compose up`

### Error de conexión a la base de datos
- Verifica el archivo `api/.env` tenga la `DATABASE_URL` correcta.
- Si usas Railway, asegúrate de que la URL sea válida.

### La web no carga
- Espera a que la API esté healthy (ver logs: `docker compose logs -f api`)
- Verifica que el puerto 3000 no esté ocupado.

### Cambios en código no se reflejan
- Los contenedores montan volúmenes, así que los cambios deberían ser inmediatos.
- Si no, reinicia: `docker compose restart`

### Para desarrollo sin Docker (opcional)
Si prefieres desarrollo local sin contenedores:

1. **API**:
   ```bash
   cd api
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   python main.py
   ```

2. **Web**:
   ```bash
   cd web
   npm install
   npm start
   ```

---

## 📝 Notas Adicionales
- La aplicación web tiene un proxy configurado para comunicarse con la API en el puerto `8000`.
- Para el procesamiento de datos de los torniquetes, coloca los archivos en `data/turnstile/`.
- Las automatizaciones de correos se gestionan externamente mediante **n8n**.
- Para más detalles, consulta `ARCHITECTURE.md` y `README.md`.
