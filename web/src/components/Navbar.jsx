// src/components/Navbar.jsx
export default function Navbar({ fecha, setFecha, clan, setClan, vistaActual, setVistaActual, theme, setTheme }) {
  const clanes = ["Todos", "Hamilton", "Thompson", "Nakamoto", "Tesla", "McCarty"];

  return (
    <header style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "12px 24px",
      background: "var(--nav-bg)",
      borderBottom: "1px solid var(--nav-border)",
      position: "sticky",
      top: 0,
      zIndex: 10,
    }}>
      <div style={{ display: "flex", gap: "20px", alignItems: "center" }}>
        <span style={{ fontWeight: 600, fontSize: 16, letterSpacing: "-0.3px", color: "var(--nav-text)" }}>
          InFoX
        </span>

        {/* View Switcher */}
        {setVistaActual && (
          <div style={{ display: "flex", background: "var(--nav-surface)", padding: "2px", borderRadius: "8px", border: "1px solid var(--nav-border)" }}>
            <button
              onClick={() => setVistaActual("asistencia")}
              style={{
                fontSize: 13,
                padding: "4px 12px",
                border: "none",
                borderRadius: "6px",
                background: vistaActual === "asistencia" ? "var(--nav-bg)" : "transparent",
                color: vistaActual === "asistencia" ? "var(--nav-text)" : "var(--nav-text-muted)",
                fontWeight: vistaActual === "asistencia" ? 500 : 400,
                boxShadow: vistaActual === "asistencia" ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
                cursor: "pointer",
                transition: "all 0.2s ease"
              }}
            >
              Asistencia
            </button>
            <button
              onClick={() => setVistaActual("correos")}
              style={{
                fontSize: 13,
                padding: "4px 12px",
                border: "none",
                borderRadius: "6px",
                background: vistaActual === "correos" ? "var(--nav-bg)" : "transparent",
                color: vistaActual === "correos" ? "var(--nav-text)" : "var(--nav-text-muted)",
                fontWeight: vistaActual === "correos" ? 500 : 400,
                boxShadow: vistaActual === "correos" ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
                cursor: "pointer",
                transition: "all 0.2s ease"
              }}
            >
              Correos
            </button>
            <button
              disabled
              style={{
                fontSize: 13,
                padding: "4px 12px",
                border: "none",
                borderRadius: "6px",
                background: "transparent",
                color: "var(--nav-text-muted)",
                cursor: "not-allowed",
                opacity: 0.5,
                display: "flex",
                alignItems: "center",
                gap: "4px"
              }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="8.5" cy="7" r="4"></circle>
                <line x1="20" y1="8" x2="20" y2="14"></line>
                <line x1="23" y1="11" x2="17" y2="11"></line>
              </svg>
              Llamar Lista
            </button>
          </div>
        )}
      </div>

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
                  : "1px solid var(--nav-border)",
                background: clan === c ? "#E6F1FB" : "var(--nav-surface)",
                color: clan === c ? "#0C447C" : "var(--nav-text-muted)",
                fontWeight: clan === c ? 500 : 400,
                cursor: "pointer",
              }}
            >
              {c === "Todos" ? "Todos" : c.charAt(0) + c.slice(1).toLowerCase()}
            </button>
          ))}
        </div>

        {/* Theme Toggle */}
        <button
          onClick={() => setTheme(theme === "light" ? "dark" : "light")}
          style={{
            background: "var(--nav-surface)",
            border: "1px solid var(--nav-border)",
            color: "var(--nav-text)",
            width: 34,
            height: 34,
            borderRadius: "50%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            transition: "all 0.2s ease",
            padding: 0,
            boxShadow: "0 1px 3px rgba(0,0,0,0.05)"
          }}
          title={theme === "light" ? "Modo Oscuro" : "Modo Claro"}
        >
          {theme === "light" ? (
             <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
               <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
             </svg>
          ) : (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="5"></circle>
              <line x1="12" y1="1" x2="12" y2="3"></line>
              <line x1="12" y1="21" x2="12" y2="23"></line>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
              <line x1="1" y1="12" x2="3" y2="12"></line>
              <line x1="21" y1="12" x2="23" y2="12"></line>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
          )}
        </button>

        {/* Selector de fecha */}
        <input
          type="date"
          value={fecha}
          onChange={e => setFecha(e.target.value)}
          style={{
            fontSize: 13,
            padding: "4px 10px",
            borderRadius: 8,
            border: "1px solid var(--nav-border)",
            background: "var(--nav-surface)",
            color: "var(--nav-text)",
            cursor: "pointer",
          }}
        />
      </div>
    </header>
  );
}
