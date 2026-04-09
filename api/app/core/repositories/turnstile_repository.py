# core/repositories/turnstile_repository.py

import pandas as pd
from datetime import datetime
from typing import List
from app.db.models import Coder, Registro
from app.db.session import SessionLocal


class TurnstileImporter:
    """Importador de archivos XLSX del torniquete"""
    
    @staticmethod
    def parse_xlsx(file_path: str) -> pd.DataFrame:
        """
        Lee y parsea el archivo XLSX del torniquete.
        
        Args:
            file_path: Ruta al archivo XLSX
            
        Returns:
            DataFrame con columnas normalizadas
        """
        df = pd.read_excel(file_path)
        
        # Normalizar nombres de columnas (case-insensitive)
        column_map = {}
        for col in df.columns:
            col_lower = col.strip().lower()
            if 'time' in col_lower:
                column_map[col] = 'timestamp'
            elif 'person' in col_lower:
                column_map[col] = 'nombre'
            elif 'id' in col_lower:
                column_map[col] = 'documento'
            elif 'status' in col_lower or 'entered/exited' in col_lower:
                column_map[col] = 'estado'
        
        df = df.rename(columns=column_map)
        
        # Asegurar que timestamp sea datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Limpiar documento (convertir a string, eliminar espacios)
        if 'documento' in df.columns:
            df['documento'] = df['documento'].astype(str).str.strip()
        
        # Normalizar estado: 'In' -> 'entrada', 'Out' -> 'salida'
        if 'estado' in df.columns:
            df['estado'] = df['estado'].astype(str).str.strip().str.lower()
            df['estado'] = df['estado'].map({
                'in': 'entrada',
                'out': 'salida',
                'entered': 'entrada',
                'exited': 'salida'
            })
        
        return df
    
    @staticmethod
    def match_with_coders(df: pd.DataFrame, db_session) -> List[Registro]:
        """
        Realiza matching de registros con coders en la base de datos.
        
        Args:
            df: DataFrame con columnas 'documento', 'timestamp', 'estado'
            db_session: Sesión de SQLAlchemy
            
        Returns:
            Lista de objetos Registro listos para insertar
        """
        # Obtener todos los coders y crear diccionario cédula -> coder
        coders = db_session.query(Coder).all()
        coder_dict = {str(c.cedula).strip(): c for c in coders}
        
        registros = []
        
        for _, row in df.iterrows():
            documento = str(row.get('documento', '')).strip()
            if not documento:
                continue
            
            # Buscar coder en el diccionario
            coder = coder_dict.get(documento)
            
            if not coder:
                continue
            
            dt = row['timestamp']
            registro = Registro(
                coder_id=coder.id,
                fecha=dt.date(),
                hora=dt.time(),
                estado_acceso=row.get('estado', 'entrada'),
                tipo_evento=None,  # Se determinará luego
                dispositivo='torniquete'
            )
            registros.append(registro)
        
        return registros
    
    @staticmethod
    def import_and_save(file_path: str, db_session = None):
        """
        Importa un archivo XLSX, hace matching y guarda registros en DB.
        
        Args:
            file_path: Ruta al archivo XLSX
            db_session: Sesión de BD (opcional, crea una si no se proporciona)
        
        Returns:
            Tuple (total_registros, registros_guardados, errores)
        """
        close_session = False
        if db_session is None:
            db_session = SessionLocal()
            close_session = True
        
        try:
            df = TurnstileImporter.parse_xlsx(file_path)
            print(f"📊 {len(df)} registros leídos del archivo")
            
            registros = TurnstileImporter.match_with_coders(df, db_session)
            print(f"🔍 {len(registros)} registros matcheados con coders")
            
            # Guardar en lote usando bulk_insert_mappings para mejor rendimiento
            if registros:
                # Convertir a dict para bulk_insert_mappings
                registros_dicts = []
                for registro in registros:
                    registros_dicts.append({
                        'coder_id': registro.coder_id,
                        'fecha': registro.fecha,
                        'hora': registro.hora,
                        'estado_acceso': registro.estado_acceso,
                        'tipo_evento': registro.tipo_evento,
                        'dispositivo': registro.dispositivo
                    })
                
                db_session.bulk_insert_mappings(Registro, registros_dicts)
                db_session.commit()
                print(f"💾 {len(registros)} registros guardados en la base de datos (bulk insert)")
            else:
                print("⚠️  No hay registros para guardar")
            
            return len(df), len(registros), []
            
        except Exception as e:
            db_session.rollback()
            raise e
        finally:
            if close_session:
                db_session.close()