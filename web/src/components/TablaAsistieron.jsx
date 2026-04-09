// src/components/TablaAsistieron.jsx
import { useFetch } from "../hooks/useFetch";
import { api }      from "../services/api";

const ESTADOS = {
  puntual:         { label: "Puntual",  color: "success" },
  retardo_leve:    { label: "Leve",     color: "warn"    },
  retardo_grave:   { label: "Grave",    color: "warn"    },
  retardo_critico: { label: "Crítico",  color: "danger"  },
};

function Badge({ tipo }) {
  const e = ESTADOS[tipo] || { label: tipo || "Puntual", color: "success" };
  const colores = {
    success: { bg: "rgba(34,197,94,.15)", text: "rgb(22,163,74)"    },
    warn:    { bg: "var(--warn-bg)",      text: "var(--warn-text)"   },
    danger:  { bg: "var(--danger-bg)",    text: "var(--danger-text)" },
  };
  const { bg, text } = colores[e.color] || colores.success;
  return (
    <span style={{
      fontSize: 11, fontWeight: 500, padding: "3px 10px",
      borderRadius: 20, background: bg, color: text,
    }}>
      {e.label}
    </span>
  );
}

function SecTitle({ children }) {
  return (
    <p style={{
      fontSize: 11, fontWeight: 500, letterSpacing: ".06em",
      textTransform: "uppercase", color: "var(--color-text-muted)",
      marginBottom: 8,
    }}>
      {children}
    </p>
  );
}

export default function TablaAsistieron({ fecha, clan }) {
  const { data, loading, error } = useFetch(
    () => api.asistieron(fecha),
    [fecha]
  );

  const filas = (data?.estudiantes || []).filter(e =>
    clan === "Todos" || e.clan === clan
  );

  return (
    <div style={{ marginBottom: 24 }}>
      <SecTitle>Asistieron hoy</SecTitle>

      {loading && <Skeleton rows={4} />}
      {error   && <Error msg={error} />}

      {!loading && !error && (
        filas.length === 0
          ? <Vacio msg="No hay registros de asistencia para este día" />
          : (
            <div style={{
              background: "var(--color-bg)",
              border: "1px solid var(--color-border)",
              borderRadius: 10,
              overflow: "hidden",
            }}>
              {/* Header */}
              <div style={rowStyle(true)}>
                <span>Estudiante</span>
                <span>Clan</span>
                <span>Hora llegada</span>
                <span>Estado entrada</span>
                <span>Retardo</span>
              </div>

              {filas.map((e, i) => (
                <div key={e.id} style={rowStyle(false, i === filas.length - 1)}>
                  <span style={{ fontWeight: 500 }}>{e.nombre}</span>
                  <span style={{ color: "var(--color-text-muted)" }}>{clanLabel(e.clan)}</span>
                  <span style={{ fontWeight: 500 }}>{e.hora_entrada || "—"}</span>
                  <span><Badge tipo={e.estado_entrada} /></span>
                  <span>
                    {e.minutos_retardo
                      ? (
                        <span style={{
                          fontSize: 11, color: "var(--warn-text)",
                          background: "var(--warn-bg)",
                          padding: "1px 6px", borderRadius: 6,
                        }}>
                          +{e.minutos_retardo} min
                        </span>
                      )
                      : <span style={{ color: "var(--color-text-muted)", fontSize: 12 }}>—</span>
                    }
                  </span>
                </div>
              ))}
            </div>
          )
      )}
    </div>
  );
}

function clanLabel(c) {
  return c ? c.charAt(0) + c.slice(1).toLowerCase() : "—";
}

function rowStyle(isHeader, isLast = false) {
  return {
    display: "grid",
    gridTemplateColumns: "1.8fr 1fr 1fr 1fr 1fr",
    padding: "9px 14px",
    fontSize: isHeader ? 11 : 13,
    fontWeight: isHeader ? 500 : 400,
    color: isHeader ? "var(--color-text-muted)" : "var(--color-text)",
    textTransform: isHeader ? "uppercase" : "none",
    letterSpacing: isHeader ? ".05em" : 0,
    background: isHeader ? "var(--color-surface)" : "var(--color-bg)",
    borderBottom: isLast ? "none" : "1px solid var(--color-border)",
    alignItems: "center",
  };
}

function Skeleton({ rows }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      {[...Array(rows)].map((_, i) => (
        <div key={i} style={{
          height: 38, borderRadius: 8,
          background: "var(--color-surface)",
          animation: "pulse 1.5s infinite",
        }} />
      ))}
    </div>
  );
}

function Error({ msg }) {
  return <p style={{ color: "var(--danger-text)", fontSize: 13 }}>Error: {msg}</p>;
}

function Vacio({ msg }) {
  return (
    <p style={{
      textAlign: "center", padding: "20px 0",
      color: "var(--color-text-muted)", fontSize: 13,
      background: "var(--color-bg)",
      border: "1px solid var(--color-border)",
      borderRadius: 10,
    }}>
      {msg}
    </p>
  );
}
