// src/components/SeccionMedio.jsx
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
      borderRadius: 20, background: bg, color: text, whiteSpace: "nowrap",
    }}>
      {children}
    </span>
  );
}

function Vacio({ msg }) {
  return (
    <p style={{
      textAlign: "center", padding: "18px 0",
      color: "var(--color-text-muted)", fontSize: 13,
      background: "var(--color-bg)",
      border: "1px solid var(--color-border)",
      borderRadius: 10,
    }}>
      {msg}
    </p>
  );
}

function MiniLista({ children }) {
  return (
    <div style={{
      background: "var(--color-bg)",
      border: "1px solid var(--color-border)",
      borderRadius: 10, overflow: "hidden",
    }}>
      {children}
    </div>
  );
}

function MiniRow({ isLast, children }) {
  return (
    <div style={{
      display: "flex", justifyContent: "space-between",
      alignItems: "center", padding: "9px 14px", fontSize: 13,
      borderBottom: isLast ? "none" : "1px solid var(--color-border)",
    }}>
      {children}
    </div>
  );
}

function ListaAusentes({ fecha, clan }) {
  const { data, loading, error } = useFetch(() => api.ausentes(fecha), [fecha]);
  const filas = (data?.estudiantes || []).filter(e =>
    clan === "Todos" || e.clan === clan
  );
  return (
    <div style={{ marginBottom: 24 }}>
      <SecTitle>Ausentes</SecTitle>
      {loading && <SkeletonList rows={3} />}
      {error && <p style={{ color: "var(--danger-text)", fontSize: 13 }}>Error: {error}</p>}
      {!loading && !error && filas.length === 0 && <Vacio msg="Sin ausencias este día" />}
      {!loading && !error && filas.length > 0 && (
        <MiniLista>
          {filas.map((e, i) => (
            <MiniRow key={e.id} isLast={i === filas.length - 1}>
              <div>
                <p style={{ margin: 0, fontWeight: 500 }}>{e.nombre}</p>
                <p style={{ margin: 0, fontSize: 11, color: "var(--color-text-muted)" }}>
                  {e.clan.charAt(0) + e.clan.slice(1).toLowerCase()}
                </p>
              </div>
              <Badge bg="var(--absent-bg)" text="var(--absent-text)">Ausente</Badge>
            </MiniRow>
          ))}
        </MiniLista>
      )}
    </div>
  );
}

function ExcesosBreak({ fecha, clan }) {
  const { data, loading, error } = useFetch(() => api.excesoBreak(fecha), [fecha]);

  // Backend retorna { excesos: [{ id, nombre, cedula, clan, descripcion, minutos, tipo_break }] }
  const todos = (data?.excesos || []).filter(e =>
    clan === "Todos" || e.clan === clan
  );
  const desayuno = todos.filter(e => e.tipo_break === "desayuno");
  const almuerzo = todos.filter(e => e.tipo_break === "almuerzo");
  const filas    = todos; // mostrar todos juntos

  return (
    <div style={{ marginBottom: 24 }}>
      <SecTitle>Excesos de break</SecTitle>
      {loading && <SkeletonList rows={3} />}
      {error && <p style={{ color: "var(--danger-text)", fontSize: 13 }}>Error: {error}</p>}
      {!loading && !error && filas.length === 0 && <Vacio msg="Sin excesos este día" />}
      {!loading && !error && filas.length > 0 && (
        <MiniLista>
          {filas.map((e, i) => {
            const esDesayuno = e.tipo_break === "desayuno";
            return (
              <MiniRow key={`${e.id}-${i}`} isLast={i === filas.length - 1}>
                <div>
                  <p style={{ margin: 0, fontWeight: 500 }}>{e.nombre}</p>
                  <p style={{ margin: 0, fontSize: 11, color: "var(--color-text-muted)" }}>
                    {esDesayuno ? "Desayuno" : "Almuerzo"} 
                    {e.minutos !== null && ` · +${e.minutos} min`}
                    {e.minutos === null && ` · ${e.descripcion || "Sin retorno"}`}
                  </p>
                </div>
                <Badge
                  bg={esDesayuno   ? "var(--warn-bg)"   : "var(--danger-bg)"}
                  text={esDesayuno ? "var(--warn-text)"  : "var(--danger-text)"}
                >
                  {esDesayuno ? "Desayuno" : "Almuerzo"}
                </Badge>
              </MiniRow>
            );
          })}
        </MiniLista>
      )}
    </div>
  );
}

export default function SeccionMedio({ fecha, clan, soloAusentes, soloBreaks }) {
  if (soloAusentes) return <ListaAusentes fecha={fecha} clan={clan} />;
  if (soloBreaks)   return <ExcesosBreak  fecha={fecha} clan={clan} />;
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 24 }}>
      <ListaAusentes fecha={fecha} clan={clan} />
      <ExcesosBreak  fecha={fecha} clan={clan} />
    </div>
  );
}

function SkeletonList({ rows }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      {[...Array(rows)].map((_, i) => (
        <div key={i} style={{
          height: 50, borderRadius: 8,
          background: "var(--color-surface)",
          animation: "pulse 1.5s infinite",
        }} />
      ))}
    </div>
  );
}
