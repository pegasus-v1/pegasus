#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models import Registro

db = SessionLocal()
try:
    count = db.query(Registro).count()
    print(f"Registros en tabla 'registros': {count}")
finally:
    db.close()