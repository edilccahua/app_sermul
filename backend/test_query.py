import sys
import os
sys.path.append("/home/edilsonc/Documents/SERMUL APP/app_sermul/backend")
from app.core.database import SessionLocal
from app.services.historial_service import HistorialService
db = SessionLocal()
svc = HistorialService(db)
ticket = svc.get_by_id("cb3cbd99-96b9-470e-8b58-348606e7dcf8")
print(f"Ejecuta: {ticket.usuario_ejecuta.nombre if ticket.usuario_ejecuta else 'None'}")
print(f"Receptor: {ticket.usuario_receptor.nombre if ticket.usuario_receptor else 'None'}")
