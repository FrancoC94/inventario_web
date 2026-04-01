from flask import Blueprint, redirect, url_for, flash, request
from docs.extensions import db
from docs.models import Repuesto, Venta, HistorialStock

ventas_bp = Blueprint('ventas', __name__)


@ventas_bp.route('/vender/<int:id>', methods=['POST'])
def vender(id):
    try:
        p    = db.session.get(Repuesto, id)
        cant = int(request.form.get('cantidad_venta', 1))

        if not p:
            flash('Repuesto no encontrado.', 'danger')
            return redirect(url_for('inventario.inicio'))

        if cant <= 0:
            flash('La cantidad debe ser mayor a 0.', 'warning')
            return redirect(url_for('inventario.inicio'))

        if p.stock < cant:
            flash(f'⚠️ Stock insuficiente. Disponible: {p.stock} uds.', 'danger')
            return redirect(url_for('inventario.inicio'))

        ganancia = (p.p_venta - p.p_costo) * cant
        venta = Venta(
            repuesto_id=p.id,
            cantidad=cant,
            total_venta=p.p_venta * cant,
            ganancia_operacion=ganancia
        )
        anterior  = p.stock
        p.stock  -= cant
        p.vendido += cant

        db.session.add(venta)
        db.session.add(HistorialStock(
            repuesto_id=p.id,
            stock_anterior=anterior,
            stock_nuevo=p.stock,
            accion='VENDIDO'
        ))
        db.session.commit()
        flash(f'✅ Venta registrada: {cant} × {p.nombre}', 'success')

    except ValueError:
        flash('❌ Cantidad inválida.', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al vender: {e}', 'danger')

    return redirect(url_for('inventario.inicio'))


@ventas_bp.route('/eliminar_venta/<int:id>')
def eliminar_venta(id):
    try:
        v = db.session.get(Venta, id)
        if not v:
            flash('Venta no encontrada.', 'danger')
            return redirect(url_for('inventario.inicio'))

        if v.repuesto:
            anterior         = v.repuesto.stock
            v.repuesto.stock += v.cantidad
            v.repuesto.vendido = max(0, v.repuesto.vendido - v.cantidad)
            db.session.add(HistorialStock(
                repuesto_id=v.repuesto.id,
                stock_anterior=anterior,
                stock_nuevo=v.repuesto.stock,
                accion='ANULADO'
            ))

        db.session.delete(v)
        db.session.commit()
        flash('↩️ Venta anulada y stock restaurado.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al anular: {e}', 'danger')

    return redirect(url_for('inventario.inicio'))