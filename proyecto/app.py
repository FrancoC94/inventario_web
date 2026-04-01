import os
from flask import Flask
from extensions import db
from flask_migrate import Migrate  # Migraciones de SQLAlchemy

def create_app():
    app = Flask(__name__)

    # ── Configuración ──────────────────────────────────────────────────────
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///driveflow.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.environ.get('SECRET_KEY', 'cambia-esto-en-produccion')

    # ── Extensiones ────────────────────────────────────────────────────────
    db.init_app(app)
    migrate = Migrate(app, db)  # Integración de Flask-Migrate

    # ── Blueprints ─────────────────────────────────────────────────────────
    from proyecto.routes.inventario import inventario_bp
    from proyecto.routes.ventas import ventas_bp
    from proyecto.routes.chat import chat_bp

    app.register_blueprint(inventario_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(chat_bp)

    return app

if __name__ == '__main__':
    application = create_app()
    application.run(host='127.0.0.1', port=5050, debug=True, use_reloader=False)