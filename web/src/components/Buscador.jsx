// src/components/Buscador.jsx
import { useState, useRef, useEffect } from "react";
import { buscar, detalleDia, historial } from "../services/api";

const ESTADO_CONFIG = {
  puntual:         { label: "Puntual",  bg: "var(--ok-bg)",      text: "var(--ok-text)"     },
  retardo_leve:    { label: "Leve",     bg: "var(--warn-bg)",    text: "var(--warn-text)"   },
  retardo_grave:   { label: "Grave",    bg: "var(--warn-bg)",    text: "var(--warn-text)"   },
  retardo_critico: { label: "Critico",  bg: "var(--danger-bg)",  text: "var(--danger-text)" },
  ausente:         { label: "Ausente",  bg: "var(--absent-bg)",  text: "var(--absent-text)" },
};

const TIPO_LABEL = {
  ENTRADA:                "Entrada",
  SALIDA:                 "Salida",
  SALIDA_BREAK_DESAYUNO:  "Salio a desayuno",
  ENTRADA_BREAK_DESAYUNO: "Regreso de desayuno",
  SALIDA_BREAK_ALMUERZO:  "Salio a almuerzo",
  ENTRADA_BREAK_ALMUERZO: "Regreso de almuerzo",
};

const DIAS_SEMANA = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"];

// Convierte cualquier formato de fecha a string YYYY-MM-DD
function toFechaStr(fecha) {
  if (!fecha) return "";
  if (typeof fecha === "string") return fecha.slice(0, 10);
  return new Date(fecha).toISOString().slice(0, 10);
}

function Badge({ estado }) {
  const e = ESTADO_CONFIG[estado] || { label: estado, bg: "var(--color-surface)", text: "var(--color-text-muted)" };
  return (
    <span style={{
      fontSize: 10, fontWeight: 500, padding: "2px 8px",
      borderRadius: 10, background: e.bg, color: e.text, whiteSpace: "nowrap",
    }}>
      {e.label}
    </span>
  );
}

function DetalleDia({ estudianteId, fechaStr }) {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    detalleDia(estudianteId, fechaStr)
      .then(d => setData(d.registros || []))
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, [estudianteId, fechaStr]);

  if (loading) return (
    <p style={{ fontSize: 12, color: "var(--color-text-muted)", padding: "8px 0" }}>
      Cargando...
    </p>
  );

  if (!data || data.length === 0) return (
    <p style={{ fontSize: 12, color: "var(--color-text-muted)", padding: "8px 0" }}>
      Sin registros este dia
    </p>
  );

  return (
    <div style={{ marginTop: 8 }}>
      {data.map((ev, i) => (
        <div key={i} style={{
          display:        "flex",
          justifyContent: "space-between",
          alignItems:     "center",
          padding:        "6px 10px",
          borderRadius:   6,
          background:     i % 2 === 0 ? "var(--color-surface)" : "transparent",
          fontSize:       12,
        }}>
          <span style={{ color: "var(--color-text-muted)", minWidth: 160 }}>
            {TIPO_LABEL[ev.tipo_evento] || ev.tipo_evento}
          </span>
          <span style={{
            fontWeight: 500,
            color: ev.direccion === "entrada" ? "var(--ok-text)" : "var(--warn-text)",
          }}>
            {ev.hora}
          </span>
        </div>
      ))}
    </div>
  );
}

function DiasToggle({ est }) {
  const [abiertos, setAbiertos] = useState({});
  const [dias, setDias] = useState(Array.isArray(est.dias) ? est.dias : null);
  const [loadingDias, setLoadingDias] = useState(false);
  const [diasError, setDiasError] = useState(null);

  const toggleDia = (fechaStr) =>
    setAbiertos(prev => ({ ...prev, [fechaStr]: !prev[fechaStr] }));

  const cargarHistorial = () => {
    if (dias !== null) return; // Ya cargado
    setLoadingDias(true);
    historial(est.id, 7)
      .then((result) => setDias(result.historial || []))
      .catch(() => {
        setDiasError("No se pudo cargar el historial");
        setDias([]);
      })
      .finally(() => setLoadingDias(false));
  };

  const diasConFecha = (dias || []).map(dia => ({
    ...dia,
    fechaStr: toFechaStr(dia.fecha),
  }));

  if (dias === null && !loadingDias) {
    return (
      <button
        onClick={cargarHistorial}
        style={{
          padding: "8px 16px",
          borderRadius: 6,
          border: "1px solid var(--color-border)",
          background: "var(--color-bg)",
          color: "var(--color-text)",
          cursor: "pointer",
          fontSize: 12,
        }}
      >
        Cargar historial de asistencia
      </button>
    );
  }

  if (loadingDias) {
    return (
      <p style={{ fontSize: 12, color: "var(--color-text-muted)", padding: "8px 0" }}>
        Cargando historial...
      </p>
    );
  }

  if (dias && dias.length === 0) {
    return (
      <p style={{ fontSize: 12, color: "var(--color-text-muted)", padding: "8px 0" }}>
        {diasError || "No hay historial disponible para este estudiante."}
      </p>
    );
  }

  return (
    <div>
      {/* Botones de días */}
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 4 }}>
        {diasConFecha.map((dia) => {
          const fecha   = new Date(dia.fechaStr + "T12:00:00");
          const nombre  = DIAS_SEMANA[fecha.getDay() - 1] || "?";
          const estado  = dia.ausente ? "ausente" : dia.estado_entrada;
          const config  = ESTADO_CONFIG[estado] || {};
          const abierto = abiertos[dia.fechaStr];

          return (
            <button
              key={dia.fechaStr}
              onClick={() => toggleDia(dia.fechaStr)}
              style={{
                display:      "flex",
                alignItems:   "center",
                gap:          6,
                padding:      "6px 12px",
                borderRadius: 20,
                border:       abierto
                                ? `1.5px solid ${config.text}`
                                : "1px solid var(--color-border)",
                background:   abierto ? config.bg : "var(--color-bg)",
                cursor:       "pointer",
                fontSize:     12,
                fontWeight:   abierto ? 500 : 400,
                color:        abierto ? config.text : "var(--color-text)",
                transition:   "all 0.2s ease",
              }}
            >
              {nombre}
              
              <span style={{
                fontSize:   9,
                opacity:    0.6,
                display:    "inline-block",
                transform:  abierto ? "rotate(180deg)" : "rotate(0deg)",
                transition: "transform 0.2s ease",
              }}>
                ▼
              </span>
            </button>
          );
        })}
      </div>

      {/* Detalle de cada día abierto */}
      {diasConFecha.map((dia) => {
        const abierto = abiertos[dia.fechaStr];
        const fecha   = new Date(dia.fechaStr + "T12:00:00");
        return (
          <div key={dia.fechaStr} style={{
            display:          "grid",
            gridTemplateRows: abierto ? "1fr" : "0fr",
            transition:       "grid-template-rows 0.3s ease",
            overflow:         "hidden",
          }}>
            <div style={{ minHeight: 0 }}>
              <div style={{
                opacity:    abierto ? 1 : 0,
                transform:  abierto ? "translateY(0)" : "translateY(-6px)",
                transition: "opacity 0.25s ease, transform 0.25s ease",
                padding:    abierto ? "4px 0 8px" : 0,
              }}>
                {abierto && (
                  <>
                    <p style={{
                      fontSize: 11, fontWeight: 500,
                      color: "var(--color-text-muted)",
                      textTransform: "uppercase",
                      letterSpacing: ".05em",
                      margin: "0 0 4px",
                    }}>
                      
                      {fecha.toLocaleDateString("es-CO", {
                        weekday: "long", day: "numeric", month: "short"
                      })}
                      {dia.minutos_retardo > 0 && (
                        <span style={{ color: "var(--warn-text)", marginLeft: 8 }}>
                          +{dia.minutos_retardo} min retardo
                        </span>
                      )}
                    </p>
                    <DetalleDia estudianteId={est.id} fechaStr={dia.fechaStr} />
                  </>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function TarjetaEstudiante({ est }) {
  return (
    <div style={{
      background:   "var(--color-bg)",
      border:       "1px solid var(--color-border)",
      borderRadius: 12,
      padding:      "16px 20px",
      marginBottom: 12,
    }}>
      <div style={{
        display:        "flex",
        justifyContent: "space-between",
        alignItems:     "flex-start",
        marginBottom:   14,
      }}>
        <div>
          <p style={{ margin: 0, fontWeight: 600, fontSize: 15 }}>{est.nombre}</p>
          <p style={{ margin: "2px 0 0", fontSize: 12, color: "var(--color-text-muted)" }}>
            {est.clan.charAt(0) + est.clan.slice(1).toLowerCase()}
          </p>
        </div>
        <div style={{ textAlign: "right" }}>
          <p style={{ margin: 0, fontSize: 12, color: "var(--color-text-muted)" }}>
            {est.incidencias} incidencia{est.incidencias !== 1 ? "s" : ""}
          </p>
          <p style={{ margin: "2px 0 0", fontSize: 12, color: "var(--color-text-muted)" }}>
            {est.promedioHoras}h activo/dia
          </p>
        </div>
      </div>

      <DiasToggle est={est} />
    </div>
  );
}

export default function Buscador({clan}) {
  const [query,      setQuery]      = useState("");
  const [resultados, setResultados] = useState(null);
  const [loading,    setLoading]    = useState(false);
  const [error,      setError]      = useState(null);
  const timerRef = useRef(null);
  const searchIdRef = useRef(0);

  const handleChange = (e) => {
    const val = e.target.value;
    setQuery(val);
    setError(null);
    clearTimeout(timerRef.current);

    if (val.trim().length < 2) {
      setResultados(null);
      return;
    }

    // Incrementar ID de búsqueda para ignorar respuestas antiguas
    const currentSearchId = ++searchIdRef.current;

    timerRef.current = setTimeout(async () => {
      // Verificar si esta búsqueda aún es la actual
      if (currentSearchId !== searchIdRef.current) return;

      setLoading(true);
      try {
        const data = await buscar(val.trim());
        // Verificar de nuevo antes de setear
        if (currentSearchId === searchIdRef.current) {
          setResultados(data.resultados || []);
        }
      } catch {
        if (currentSearchId === searchIdRef.current) {
          setError("Error al buscar");
        }
      } finally {
        if (currentSearchId === searchIdRef.current) {
          setLoading(false);
        }
      }
    }, 800);
  };

  const limpiar = () => {
    setQuery("");
    setResultados(null);
    setError(null);
  };

  return (
    <div style={{ width: "100%", maxWidth: 600, margin: "0 auto" }}>
      <div style={{ position: "relative", marginBottom: 16 }}>
        <input
          type="text"
          value={query}
          onChange={handleChange}
          placeholder="Buscar estudiante..."
          style={{
            width:        "100%",
            padding:      "12px 44px 12px 18px",
            borderRadius: 28,
            border:       "1px solid var(--color-border)",
            background:   "var(--color-bg)",
            fontSize:     14,
            color:        "var(--color-text)",
            outline:      "none",
            boxSizing:    "border-box",
            transition:   "border 0.2s",
          }}
          onFocus={e => e.target.style.border = "1.5px solid #378ADD"}
          onBlur={e  => e.target.style.border = "1px solid var(--color-border)"}
        />
        {query && (
          <button
            onClick={limpiar}
            style={{
              position:   "absolute", right: 14, top: "50%",
              transform:  "translateY(-50%)",
              background: "none", border: "none",
              cursor:     "pointer", fontSize: 16,
              color:      "var(--color-text-muted)", lineHeight: 1,
            }}
          >
            x
          </button>
        )}
      </div>

      {loading && (
        <p style={{ textAlign: "center", fontSize: 13, color: "var(--color-text-muted)" }}>
          Buscando...
        </p>
      )}
      {error && (
        <p style={{ textAlign: "center", fontSize: 13, color: "var(--danger-text)" }}>
          {error}
        </p>
      )}
      {!loading && resultados !== null && resultados.length === 0 && (
        <p style={{ textAlign: "center", fontSize: 13, color: "var(--color-text-muted)" }}>
          No se encontro ningun estudiante
        </p>
      )}
      {!loading && resultados && resultados
  .filter(est => clan === "Todos" || est.clan === clan)
  .map(est => (
    <TarjetaEstudiante key={est.id} est={est} />
      ))}
    </div>
  );
}
