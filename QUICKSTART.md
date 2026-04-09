# 🚀 Pegasus - Quick Start Guide

Bienvenido al proyecto **Pegasus**. Esta guía te ayudará a poner en marcha tanto la API como la Web en pocos minutos.

## 📋 Requisitos Previos

Asegúrate de tener instalado:
- **Python 3.10+**
- **Node.js (v18+)** y npm
- **PostgreSQL** (opcional local, el proyecto usa Railway por defecto)

---

## 🛠️ 1. Configuración de la API (Python)

El backend utiliza FastAPI para la lógica principal y el procesamiento de datos.

1. **Navega a la carpeta de la api:**
   ```bash
   cd api
   ```

2. **Crea un entorno virtual:**
   ```bash
   python -m venv venv
   ```

3. **Activa el entorno virtual:**
   - **Windows:** `.\venv\Scripts\activate`
   - **Mac/Linux:** `source venv/bin/activate`

4. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configura el entorno:**
   Verifica que el archivo `.env` tenga la `DATABASE_URL` correcta.

6. **Inicia el servidor:**
   ```bash
   python main.py
   ```
   > La API estará disponible en `http://localhost:8000`

---

## 💻 2. Configuración de la Web (React)

El frontend es un dashboard moderno construido con React.

1. **Navega a la carpeta web:**
   ```bash
   cd web
   ```

2. **Instala las dependencias:**
   ```bash
   npm install
   ```

3. **Inicia la aplicación:**
   ```bash
   npm start
   ```
   > La aplicación se abrirá en `http://localhost:3000`

---

## 📝 Notas Adicionales
- La aplicación web tiene un proxy configurado para comunicarse con la API en el puerto `8000`.
- Para el procesamiento de datos de los torniquetes, coloca los archivos CSV en `data/turnstile/`.
- Las automatizaciones de correos se gestionan externamente mediante **n8n**.
