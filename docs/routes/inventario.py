from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import func
from datetime import datetime
from docs.extensions import db
from docs.models import Repuesto, Venta, HistorialStock

inventario_bp = Blueprint('inventario', __name__)

# ── Helpers ─────────────────────────────────────────────────────────────
def _registrar_historial(repuesto_id, stock_anterior, stock_nuevo, accion):
    db.session.add(HistorialStock(
        repuesto_id=repuesto_id,
        stock_anterior=stock_anterior,
        stock_nuevo=stock_nuevo,
        accion=accion
    ))

def _stats_dashboard():
    hoy = datetime.utcnow().date()
    ventas_hoy  = Venta.query.filter(func.date(Venta.fecha) == hoy).all()
    total_hoy   = sum(v.total_venta for v in ventas_hoy)
    top = (
        db.session.query(Venta.repuesto_id, func.sum(Venta.ganancia_operacion).label('g'))
        .group_by(Venta.repuesto_id)
        .order_by(db.text('g DESC'))
        .first()
    )
    estrella = db.session.get(Repuesto, top[0]).nombre if top else 'Sin datos'
    todos         = Repuesto.query.all()
    faltantes     = [p for p in todos if p.stock < 10]
    inversion_stock     = sum(p.p_costo * p.stock for p in todos)
    ganancia_acumulada  = db.session.query(func.sum(Venta.ganancia_operacion)).scalar() or 0
    inversion_sugerida  = sum((10 - p.stock) * p.p_costo for p in faltantes)

    return dict(
        total_hoy=total_hoy,
        estrella=estrella,
        inversion=inversion_stock,
        ganancia=ganancia_acumulada,
        inversion_sugerida=inversion_sugerida,
        alertas=[p for p in todos if p.stock < 5],
    )

# ── Rutas ───────────────────────────────────────────────────────────────
@inventario_bp.route('/')
def inicio():
    busqueda = request.args.get('buscar', '').upper().strip()
    inventario = (
        Repuesto.query.filter(func.upper(Repuesto.nombre).contains(busqueda)).all()
        if busqueda else Repuesto.query.all()
    )
    ultimas_ventas = Venta.query.order_by(Venta.fecha.desc()).limit(15).all()
    return render_template(
        'index.html',
        inventario=inventario,
        ventas=ultimas_ventas,
        **_stats_dashboard()
    )

@inventario_bp.route('/agregar', methods=['POST'])
def agregar():
    try:
        nombre  = request.form['nombre'].upper().strip()
        p_costo = float(request.form['p_costo'])
        p_venta = float(request.form['p_venta'])
        stock   = int(request.form['stock'])

        if p_costo <= 0 or p_venta <= 0 or stock < 0:
            flash('Los valores deben ser positivos.', 'warning')
            return redirect(url_for('inventario.inicio'))

        p = Repuesto.query.filter_by(nombre=nombre).first()
        if p:
            anterior = p.stock
            p.stock  += stock
            p.p_costo = p_costo
            p.p_venta = p_venta
            _registrar_historial(p.id, anterior, p.stock, 'AGREGADO')
        else:
            p = Repuesto(nombre=nombre, p_costo=p_costo, p_venta=p_venta, stock=stock)
            db.session.add(p)
            db.session.flush()
            _registrar_historial(p.id, 0, stock, 'AGREGADO')

        db.session.commit()
        flash(f'✅ Operación exitosa: {nombre}', 'success')

    except ValueError:
        flash('❌ Los campos numéricos tienen un formato incorrecto.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error inesperado: {e}', 'danger')

    return redirect(url_for('inventario.inicio'))

# (Resto de rutas: editar, eliminar, subir masivo y exportar compras igual que tu código)