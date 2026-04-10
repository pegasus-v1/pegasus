// src/App.jsx
import { useState, useEffect } from "react";
import Navbar          from "./components/Navbar";
// import AsistenteIA     from "./components/AsistenteIA";
import TarjetasResumen from "./components/TarjetasResumen";
import TablaTarde      from "./components/TablaTarde";
import SeccionMedio    from "./components/SeccionMedio";
import TablaSalidas    from "./components/TablaSalidas";
import TablaAsistieron from "./components/TablaAsistieron";
import Buscador        from "./components/Buscador";
import DashboardCorreos from "./pages/DashboardCorreos";

export default function App() {
  const [fecha, setFecha] = useState("2026-01-14");
  const [clan,  setClan]  = useState("Todos");
  const [vistaActual, setVistaActual] = useState("asistencia");

  const [abiertas, setAbiertas] = useState({
    tarde:      false,
    ausentes:   false,
    breaks:     false,
    salidas:    false,
    asistieron: false,
  });

  const toggle = (key) =>
    setAbiertas(prev => ({ ...prev, [key]: !prev[key] }));

  const hayAlgoAbierto = Object.values(abiertas).some(Boolean);

  return (
    <div style={{ minHeight: "100vh" }}>
      <Navbar
        fecha={fecha} setFecha={setFecha}
        clan={clan}   setClan={setClan}
        vistaActual={vistaActual} setVistaActual={setVistaActual}
      />

      <main style={{
        maxWidth:      900,
        margin:        "0 auto",
        padding:       "0 20px 40px",
        display:       "flex",
        flexDirection: "column",
        alignItems:    "center",
      }}>

        {vistaActual === "correos" ? (
          <div style={{ width: "100%", marginTop: "32px", animation: "fadeIn 0.3s ease" }}>
            <DashboardCorreos fecha={fecha} clan={clan} />
          </div>
        ) : (
          <>
            {/* Titulo centrado */}
            <div style={{
              textAlign:    "center",
              transition:   "margin 0.4s ease",
              marginTop:    hayAlgoAbierto ? "32px" : "15vh",
              marginBottom: "20px",
              width:        "100%",
            }}>
              <h1 style={{
                fontSize:      48,
                fontWeight:    600,
                letterSpacing: "-1.5px",
                color:         "var(--color-text)",
                margin:        "0 0 20px",
              }}>
                 InFoX
              </h1>

              {/* Buscador */}
              <Buscador clan={clan}/>

              <p style={{
                fontSize:   12,
                color:      "var(--color-text-muted)",
                margin:     "16px 0 0",
              }}>
                {fecha}{clan !== "Todos" && ` · ${clan.charAt(0) + clan.slice(1).toLowerCase()}`}
              </p>
            </div>

            {/* Botones toggle */}
            <TarjetasResumen
              fecha={fecha}
              clan={clan}
              abiertas={abiertas}
              toggle={toggle}
            />

            {/* Secciones desplegables */}
            <div style={{ width: "100%", marginTop: 8 }}>
              <Seccion visible={abiertas.tarde}>
                <TablaTarde fecha={fecha} clan={clan} />
              </Seccion>
              <Seccion visible={abiertas.ausentes}>
                <SeccionMedio fecha={fecha} clan={clan} soloAusentes />
              </Seccion>
              <Seccion visible={abiertas.breaks}>
                <SeccionMedio fecha={fecha} clan={clan} soloBreaks />
              </Seccion>
              <Seccion visible={abiertas.salidas}>
                <TablaSalidas fecha={fecha} clan={clan} />
              </Seccion>
              <Seccion visible={abiertas.asistieron}>
                <TablaAsistieron fecha={fecha} clan={clan} />
              </Seccion>
            </div>
          </>
        )}
      </main>
      {/* <AsistenteIA /> */}
    </div>
  );
}

function Seccion({ visible, children }) {
  // Monta los hijos la primera vez que se abre, y los mantiene vivos
  const [estaViva, setEstaViva] = useState(false);
  useEffect(() => {
    if (visible && !estaViva) setEstaViva(true);
  }, [visible, estaViva]);

  return (
    <div style={{
      display:          "grid",
      gridTemplateRows: visible ? "1fr" : "0fr",
      transition:       "grid-template-rows 0.35s ease",
      overflow:         "hidden",
    }}>
      <div style={{ minHeight: 0 }}>
        {estaViva && (
          <div style={{
            paddingTop: visible ? 4  : 0,
            opacity:    visible ? 1  : 0,
            transform:  visible ? "translateY(0)" : "translateY(-8px)",
            transition: "opacity 0.3s ease 0.05s, transform 0.3s ease 0.05s",
          }}>
            {children}
          </div>
        )}
      </div>
    </div>
  );
}
