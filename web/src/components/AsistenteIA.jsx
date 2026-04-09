// src/components/AsistenteIA.jsx
import { useState } from "react";

export default function AsistenteIA() {
  const [activo, setActivo] = useState(false);

  return (
    <div style={{ position: "fixed", bottom: 32, right: 32, zIndex: 1000 }}>
      {/* Estilos dinámicos para animaciones */}
      <style>
        {`
          @keyframes ai-float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-6px); }
            100% { transform: translateY(0px); }
          }
          @keyframes ai-glow {
            0% { box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4); }
            50% { box-shadow: 0 8px 30px rgba(168, 85, 247, 0.6); }
            100% { box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4); }
          }
          .ai-button-premium:hover {
            transform: scale(1.1) !important;
            filter: brightness(1.1);
          }
        `}
      </style>

      {/* Panel del asistente — Estilo Glassmorphism */}
      {activo && (
        <div style={{
          position: "absolute",
          bottom: "calc(100% + 16px)",
          right: 0,
          width: 300,
          padding: "20px",
          background: "rgba(255, 255, 255, 0.8)",
          backdropFilter: "blur(12px)",
          WebkitBackdropFilter: "blur(12px)",
          border: "1px solid rgba(255, 255, 255, 0.3)",
          borderRadius: "20px",
          boxShadow: "0 10px 40px rgba(0,0,0,0.1)",
          animation: "ai-float 4s ease-in-out infinite",
        }}>
          <div style={{ 
            display: "flex", 
            alignItems: "center", 
            gap: 10, 
            marginBottom: 12 
          }}>
            <div style={{
              width: 8, height: 8, borderRadius: "50%", background: "#6366F1"
            }} />
            <h3 style={{ 
              fontSize: 14, 
              fontWeight: 600, 
              margin: 0, 
              color: "#1e293b" 
            }}>Pegasus AI</h3>
          </div>
          
          <p style={{ fontSize: 13, color: "#475569", lineHeight: 1.5, margin: 0 }}>
            Hola, soy tu asistente inteligente. Próximamente podrás preguntarme por voz detalles de asistencia o incidencias.
          </p>
          
          <div style={{ 
            marginTop: 16, 
            paddingTop: 12, 
            borderTop: "1px solid rgba(0,0,0,0.05)",
            fontSize: 11,
            color: "#94a3b8",
            fontStyle: "italic"
          }}>
            "¿Quién llegó tarde hoy en el clan Nakamoto?"
          </div>
        </div>
      )}

      {/* Botón flotante Premium */}
      <button
        className="ai-button-premium"
        onClick={() => setActivo(a => !a)}
        style={{
          width: 56,
          height: 56,
          borderRadius: "18px", // Squircle-ish
          border: "none",
          background: "linear-gradient(135deg, #6366F1 0%, #A855F7 100%)",
          color: "white",
          fontSize: 24,
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          transition: "all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)",
          animation: "ai-glow 3s ease-in-out infinite",
          outline: "none",
        }}
      >
        {activo ? (
          <span style={{ fontSize: 20 }}>✕</span>
        ) : (
          <img 
            src="/fox_logo.png" 
            alt="AI Fox" 
            style={{ 
              width: 32, 
              height: 32, 
              objectFit: "contain",
              filter: "drop-shadow(0 0 8px rgba(255,255,255,0.3))" 
            }} 
          />
        )}
      </button>
    </div>
  );
}
