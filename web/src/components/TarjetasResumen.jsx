// src/components/TarjetasResumen.jsx
import { useFetch } from "../hooks/useFetch";
import { api }      from "../services/api";

const CONFIG = [
  { key: "tarde",      label: "Tarde",      color: "warn"    },
  { key: "ausentes",   label: "Ausentes",   color: "danger"  },
  { key: "breaks",     label: "Breaks",     color: "warn"    },
  { key: "salidas",    label: "Salidas",    color: "warn"    },
  { key: "asistieron", label: "Asistieron", color: "success" },
];

const COLORES = {
  warn:    { bg: "var(--warn-bg)",          text: "var(--warn-text)"   },
  danger:  { bg: "var(--danger-bg)",        text: "var(--danger-text)" },
  success: { bg: "rgba(34,197,94,.15)",     text: "rgb(22,163,74)"     },
};

export default function TarjetasResumen({ fecha, clan, abiertas, toggle }) {
  const { data, loading } = useFetch(() => api.resumenDia(fecha), [fecha]);

  const clanes   = data?.por_clan || [];
  const filtrado = clan === "Todos" 
    ? clanes 
    : clanes.filter(c => c.clan.toLowerCase() === clan.toLowerCase());

  const conRetardo     = filtrado.reduce((s, c) => s + Number(c.con_retardo          || 0), 0);
  const ausentes       = filtrado.reduce((s, c) => s + Number(c.ausentes             || 0), 0);
  const salidasAnticip = filtrado.reduce((s, c) => s + Number(c.salidas_anticipadas  || 0), 0);
  const asistieron     = filtrado.reduce((s, c) => s + Number(c.coders_con_registros || 0), 0);
  const excesosBreak   = filtrado.reduce((s, c) => s + Number(c.excesos_break       || 0), 0);

  const valores = {
    tarde:      conRetardo,
    ausentes:   ausentes,
    breaks:     excesosBreak,
    salidas:    salidasAnticip,
    asistieron: asistieron,
  };

  return (
    <div style={{
      display:        "flex",
      gap:            10,
      justifyContent: "center",
      flexWrap:       "wrap",
    }}>
      {CONFIG.map(({ key, label, color }) => {
        const abierto      = abiertas[key];
        const { bg, text } = COLORES[color];
        const valor        = loading ? "…" : (valores[key] ?? 0);

        return (
          <button
            key={key}
            onClick={() => toggle(key)}
            style={{
              display:        "flex",
              alignItems:     "center",
              gap:            8,
              padding:        "8px 18px",
              borderRadius:   24,
              border:         abierto
                                ? `1.5px solid ${text}`
                                : "1px solid var(--color-border)",
              background:     abierto ? bg : "var(--color-bg)",
              cursor:         "pointer",
              transition:     "all 0.2s ease",
              fontSize:       13,
              fontWeight:     abierto ? 500 : 400,
              color:          abierto ? text : "var(--color-text)",
            }}
          >
            {/* Número badge */}
            <span style={{
              fontSize:     11,
              fontWeight:   600,
              padding:      "1px 7px",
              borderRadius: 12,
              background:   bg,
              color:        text,
              minWidth:     20,
              textAlign:    "center",
            }}>
              {valor}
            </span>

            {label}

            {/* Flecha */}
            <span style={{
              fontSize: 9,
              opacity:  0.6,
              color:    abierto ? text : "var(--color-text-muted)",
              transition: "transform 0.25s ease",
              display: "inline-block",
              transform: abierto ? "rotate(180deg)" : "rotate(0deg)",
            }}>
              ▼
            </span>
          </button>
        );
      })}
    </div>
  );
}
