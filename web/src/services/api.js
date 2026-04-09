// src/services/api.js
// Llamadas a la API de Pegasus (FastAPI)

const BASE = "/api";
const API_KEY = "mvp-test-key-123";  // Clave API para autenticación

async function get(url) {
  const res = await fetch(url, {
    headers: {
      "X-API-Key": API_KEY
    }
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Error ${res.status}: ${url} - ${errorText}`);
  }
  return res.json();
}

export const api = {
  // Reportes del día (rutas compatibles)
  resumenDia:        (fecha) => get(`${BASE}/reportes/resumen-dia?fecha=${fecha}`),
  llegaronTarde:     (fecha) => get(`${BASE}/reportes/tarde?fecha=${fecha}`),
  ausentes:          (fecha) => get(`${BASE}/reportes/ausentes?fecha=${fecha}`),
  fugaManana:        (fecha) => get(`${BASE}/reportes/fuga-manana?fecha=${fecha}`),
  excesoBreak:       (fecha, tipo = "ambos") => get(`${BASE}/reportes/exceso-break?fecha=${fecha}&tipo=${tipo}`),
  salidasAnticipadas:(fecha) => get(`${BASE}/reportes/salidas-anticipadas?fecha=${fecha}`),
  asistieron:        (fecha) => get(`${BASE}/reportes/asistieron?fecha=${fecha}`),

  // Estudiantes (nuevas rutas en /coders/)
  estudiantes:       ()      => get(`${BASE}/coders/estudiantes`),
  historial:         (id)    => get(`${BASE}/coders/estudiantes/${id}/historial`),
};

// Búsqueda (nuevas rutas en /coders/)
export const buscar = (q) => get(`${BASE}/coders/buscar?q=${encodeURIComponent(q)}`);
export const detalleDia = (id, fecha) =>
  get(`${BASE}/coders/buscar/detalle?id=${id}&fecha=${fecha}`);