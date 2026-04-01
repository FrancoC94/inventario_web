# reset_db.py
import os
import shutil
from app import create_app
from extensions import db
from models import Repuesto

# ── Confirmación ───────────────────────────────
confirm = input("⚠️ Esto eliminará toda la base de datos actual. ¿Continuar? (s/n): ")
if confirm.lower() != 's':
    print("❌ Operación cancelada.")
    exit()

# ── Respaldo automático ────────────────────────
if os.path.exists("driveflow.db"):
    shutil.copy("driveflow.db", "driveflow_backup.db")
    print("💾 Respaldo guardado como driveflow_backup.db")

# ── Reinicio de base de datos ─────────────────
app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    print("✅ Base de datos creada correctamente")

    # ── Datos de ejemplo ───────────────────────
    ejemplos = [
        Repuesto(nombre="Filtro de aire", p_costo=15.0, p_venta=25.0, stock=50),
        Repuesto(nombre="Aceite motor 5W30", p_costo=10.0, p_venta=18.0, stock=100),
        Repuesto(nombre="Bujía estándar", p_costo=3.5, p_venta=7.0, stock=200),
        Repuesto(nombre="Correa de distribución", p_costo=50.0, p_venta=85.0, stock=20),
    ]
    db.session.add_all(ejemplos)
    db.session.commit()
    print("🛠 Datos de ejemplo cargados correctamente")