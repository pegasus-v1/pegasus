// src/components/Navbar.jsx
export default function Navbar({ fecha, setFecha, clan, setClan }) {
  const clanes = ["Todos", "Hamilton", "Thompson", "Nakamoto", "Tesla", "McCarty"];

  return (
    <header style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "12px 24px",
      background: "var(--color-bg)",
      borderBottom: "1px solid var(--color-border)",
      position: "sticky",
      top: 0,
      zIndex: 10,
    }}>
      <span style={{ fontWeight: 600, fontSize: 16, letterSpacing: "-0.3px" }}>
        Panel de asistencia
      </span>

      <div style={{ display: "flex", gap: 10, alignItems: "center" }}>

        {/* Filtro por clan */}
        <div style={{ display: "flex", gap: 4 }}>
          {clanes.map(c => (
            <button
              key={c}
              onClick={() => setClan(c)}
              style={{
                fontSize: 12,
                padding: "4px 12px",
                borderRadius: 20,
                border: clan === c
                  ? "1px solid #378ADD"
                  : "1px solid var(--color-border)",
                background: clan === c ? "#E6F1FB" : "var(--color-surface)",
                color: clan === c ? "#0C447C" : "var(--color-text-muted)",
                fontWeight: clan === c ? 500 : 400,
                cursor: "pointer",
              }}
            >
              {c === "Todos" ? "Todos" : c.charAt(0) + c.slice(1).toLowerCase()}
            </button>
          ))}
        </div>

        {/* Selector de fecha */}
        <input
          type="date"
          value={fecha}
          onChange={e => setFecha(e.target.value)}
          style={{
            fontSize: 13,
            padding: "4px 10px",
            borderRadius: 8,
            border: "1px solid var(--color-border)",
            background: "var(--color-surface)",
            color: "var(--color-text)",
            cursor: "pointer",
          }}
        />
      </div>
    </header>
  );
}
