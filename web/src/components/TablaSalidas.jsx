// src/components/TablaSalidas.jsx
import { useFetch } from "../hooks/useFetch";
import { api }      from "../services/api";

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

function Badge({ bg, text, children }) {
  return (
    <span style={{
      fontSize: 11, fontWeight: 500, padding: "3px 10px",
      borderRadius: 20, background: bg, color: text,
    }}>
      {children}
    </span>
  );
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

function rowStyle(isHeader, isLast = false) {
  return {
    display: "grid",
    gridTemplateColumns: "2fr 1fr 1.5fr 1fr",
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

export default function TablaSalidas({ fecha, clan }) {
  const { data, loading, error } = useFetch(
    () => api.salidasAnticipadas(fecha),
    [fecha]
  );

  const filas = (data?.estudiantes || []).filter(e =>
    clan === "Todos" || e.clan === clan
  );

  return (
    <div style={{ marginBottom: 32 }}>
      <SecTitle>Salidas anticipadas</SecTitle>

      {loading && <Skeleton />}
      {error   && <p style={{ color: "var(--danger-text)", fontSize: 13, padding: 10 }}>Error: {error}</p>}

      {!loading && !error && (
        filas.length === 0
          ? <Vacio msg="Sin salidas anticipadas este día" />
          : (
            <div style={{
              background: "var(--color-bg)",
              border: "1px solid var(--color-border)",
              borderRadius: 10,
              overflow: "hidden",
            }}>
              <div style={rowStyle(true)}>
                <span>Estudiante</span>
                <span>Clan</span>
                <span>Hora salida</span>
                <span>Tipo</span>
              </div>

              {filas.map((e, i) => {
                const inferida = e.salida_inferida === 1 || e.salida_inferida === true;
                return (
                  <div key={e.id} style={rowStyle(false, i === filas.length - 1)}>
                    <span style={{ fontWeight: 500 }}>{e.nombre}</span>
                    <span style={{ color: "var(--color-text-muted)" }}>
                      {e.clan.charAt(0) + e.clan.slice(1).toLowerCase()}
                    </span>
                   <span>
  {inferida ? (
    <span style={{ color: "var(--color-text-muted)", fontSize: 12 }}>
      Sin registro
    </span>
  ) : (
    <>
      <span style={{ fontWeight: 500 }}>{e.hora_salida || "—"}</span>
      {e.minutos_antes > 0 && (
        <span style={{
          marginLeft: 6, fontSize: 11,
          color: "var(--danger-text)",
          background: "var(--danger-bg)",
          padding: "1px 6px", borderRadius: 6,
        }}>
          -{e.minutos_antes} min
        </span>
      )}
    </>
  )}
</span>
                    <span>
                      {inferida
                        ? <Badge bg="var(--absent-bg)"  text="var(--absent-text)">Fuga inferida</Badge>
                        : <Badge bg="var(--danger-bg)"  text="var(--danger-text)">Anticipada</Badge>
                      }
                    </span>
                  </div>
                );
              })}
            </div>
          )
      )}
    </div>
  );
}

function Skeleton() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      {[...Array(3)].map((_, i) => (
        <div key={i} style={{
          height: 38, borderRadius: 8,
          background: "var(--color-surface)",
          animation: "pulse 1.5s infinite",
        }} />
      ))}
    </div>
  );
}
