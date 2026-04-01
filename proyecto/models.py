from datetime import datetime
from proyecto.extensions import db

class Repuesto(db.Model):
    __tablename__ = 'repuesto'

    id      = db.Column(db.Integer, primary_key=True)
    nombre  = db.Column(db.String(100), nullable=False, unique=True)
    p_costo = db.Column(db.Float, nullable=False)
    p_venta = db.Column(db.Float, nullable=False)
    stock   = db.Column(db.Integer, nullable=False, default=0)
    vendido = db.Column(db.Integer, default=0)

    ventas   = db.relationship(
        'Venta', backref='repuesto',
        cascade='all, delete-orphan', lazy=True
    )
    historial = db.relationship(
        'HistorialStock', backref='repuesto',
        cascade='all, delete-orphan', lazy=True
    )

    def __repr__(self):
        return f'<Repuesto {self.nombre}>'


class Venta(db.Model):
    __tablename__ = 'venta'

    id                 = db.Column(db.Integer, primary_key=True)
    repuesto_id        = db.Column(db.Integer, db.ForeignKey('repuesto.id', ondelete='CASCADE'), nullable=False)
    cantidad           = db.Column(db.Integer, nullable=False)
    total_venta        = db.Column(db.Float, nullable=False)
    ganancia_operacion = db.Column(db.Float, nullable=False)
    fecha              = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Venta {self.id} | {self.total_venta}>'


class HistorialStock(db.Model):
    __tablename__ = 'historial_stock'

    id             = db.Column(db.Integer, primary_key=True)
    repuesto_id    = db.Column(db.Integer, db.ForeignKey('repuesto.id', ondelete='CASCADE'), nullable=False)
    fecha          = db.Column(db.DateTime, default=datetime.utcnow)
    stock_anterior = db.Column(db.Integer, nullable=False)
    stock_nuevo    = db.Column(db.Integer, nullable=False)
    accion         = db.Column(db.String(50), nullable=False)  # Ej: 'AGREGADO', 'VENDIDO', 'EDITADO'

    def __repr__(self):
        return f'<Historial {self.accion} | {self.repuesto.nombre}>'