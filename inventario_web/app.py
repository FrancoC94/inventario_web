from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///driveflow_final.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'driveflow_pro_key_2026'

db = SQLAlchemy(app)


# --- MODELOS DE BASE DE DATOS ---

class Repuesto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    p_costo = db.Column(db.Float, nullable=False)
    p_venta = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    vendido = db.Column(db.Integer, default=0)
    ventas = db.relationship('Venta', backref='repuesto', cascade="all, delete-orphan", lazy=True)


class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repuesto_id = db.Column(db.Integer, db.ForeignKey('repuesto.id', ondelete="CASCADE"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    total_venta = db.Column(db.Float, nullable=False)
    ganancia_operacion = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)


# --- RUTAS DE INTELIGENCIA Y NAVEGACIÓN ---

@app.route('/')
def inicio():
    busqueda = request.args.get('buscar', '').upper()
    lista = Repuesto.query.filter(Repuesto.nombre.contains(busqueda)).all() if busqueda else Repuesto.query.all()

    # 1. Ventas de Hoy (Corte de Caja)
    hoy = datetime.utcnow().date()
    ventas_hoy = Venta.query.filter(func.date(Venta.fecha) == hoy).all()
    total_hoy = sum(v.total_venta for v in ventas_hoy)

    # 2. Producto Estrella (Basado en Ganancia Neta)
    top = db.session.query(Venta.repuesto_id, func.sum(Venta.ganancia_operacion).label('g_total')) \
        .group_by(Venta.repuesto_id).order_by(db.text('g_total DESC')).first()
    estrella = Repuesto.query.get(top[0]).nombre if top else "Sin datos"

    # 3. Análisis de Reposición
    alertas = Repuesto.query.filter(Repuesto.stock < 5).all()
    faltantes = Repuesto.query.filter(Repuesto.stock < 10).all()
    inversion_sugerida = sum((10 - p.stock) * p.p_costo for p in faltantes)

    # 4. KPIs Globales
    inversion_stock = sum(p.p_costo * p.stock for p in Repuesto.query.all())
    ganancia_acumulada = db.session.query(func.sum(Venta.ganancia_operacion)).scalar() or 0
    ultimas_ventas = Venta.query.order_by(Venta.fecha.desc()).limit(15).all()

    return render_template('index.html',
                           inventario=lista, alertas=alertas, ventas=ultimas_ventas,
                           inversion=inversion_stock, ganancia=ganancia_acumulada,
                           total_hoy=total_hoy, estrella=estrella,
                           inversion_sugerida=inversion_sugerida)


@app.route('/exportar_compras')
def exportar_compras():
    faltantes = Repuesto.query.filter(Repuesto.stock < 10).all()
    if not faltantes: return "✅ Inventario al día. No hay pedidos pendientes."

    msg = "🛒 *PEDIDO DRIVEFLOW PRO*\n" + "-" * 20 + "\n"
    total = 0
    for p in faltantes:
        pedir = 10 - p.stock
        msg += f"• {p.nombre}: Pedir {pedir} (Stock: {p.stock})\n"
        total += (pedir * p.p_costo)
    msg += f"\n💰 *Inversión aprox:* ${total:,.2f}"
    return msg


# --- GESTIÓN CRUD (PRODUCTOS Y VENTAS) ---

@app.route('/agregar', methods=['POST'])
def agregar():
    try:
        nombre = request.form['nombre'].upper().strip()
        p = Repuesto.query.filter_by(nombre=nombre).first()
        if p:
            p.stock += int(request.form['stock'])
            flash(f"Stock actualizado: {nombre}", "info")
        else:
            nuevo = Repuesto(nombre=nombre, p_costo=float(request.form['p_costo']),
                             p_venta=float(request.form['p_venta']), stock=int(request.form['stock']))
            db.session.add(nuevo)
            flash(f"Nuevo ingreso: {nombre}", "success")
        db.session.commit()
    except:
        flash("Error al procesar el formulario", "danger")
    return redirect(url_for('inicio'))


@app.route('/editar/<int:id>', methods=['POST'])
def editar(id):
    p = Repuesto.query.get_or_404(id)
    try:
        p.nombre = request.form['nombre'].upper().strip()
        p.p_costo = float(request.form['p_costo'])
        p.p_venta = float(request.form['p_venta'])
        p.stock = int(request.form['stock'])
        db.session.commit()
        flash("Datos actualizados", "success")
    except:
        flash("Error en la edición", "danger")
    return redirect(url_for('inicio'))


@app.route('/eliminar_producto/<int:id>')
def eliminar_producto(id):
    p = Repuesto.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash("Producto eliminado del sistema", "warning")
    return redirect(url_for('inicio'))


@app.route('/vender/<int:id>', methods=['POST'])
def vender(id):
    p = Repuesto.query.get_or_404(id)
    cant = int(request.form.get('cantidad_venta', 1))
    if p.stock >= cant:
        ganancia = (p.p_venta - p.p_costo) * cant
        venta = Venta(repuesto_id=p.id, cantidad=cant, total_venta=p.p_venta * cant, ganancia_operacion=ganancia)
        p.stock -= cant
        p.vendido += cant
        db.session.add(venta)
        db.session.commit()
        flash("Venta exitosa", "success")
    else:
        flash("¡Sin Stock!", "danger")
    return redirect(url_for('inicio'))


@app.route('/eliminar_venta/<int:id>')
def eliminar_venta(id):
    v = Venta.query.get_or_404(id)
    v.repuesto.stock += v.cantidad
    v.repuesto.vendido -= v.cantidad
    db.session.delete(v)
    db.session.commit()
    flash("Venta anulada. Stock devuelto.", "info")
    return redirect(url_for('inicio'))


@app.route('/subir_masivo', methods=['POST'])
def subir_masivo():
    file = request.files.get('archivo_excel')
    if file:
        try:
            df = pd.read_excel(file)
            for _, r in df.iterrows():
                nom = str(r['nombre']).upper().strip()
                p = Repuesto.query.filter_by(nombre=nom).first()
                if p:
                    p.stock += int(r['stock'])
                else:
                    db.session.add(Repuesto(nombre=nom, p_costo=float(r['p_costo']), p_venta=float(r['p_venta']),
                                            stock=int(r['stock'])))
            db.session.commit()
            flash("Carga de Excel completada", "success")
        except:
            flash("Formato de Excel incorrecto", "danger")
    return redirect(url_for('inicio'))


@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get("msg", "").upper()
    p = Repuesto.query.filter(Repuesto.nombre.contains(msg)).first()
    res = f"📍 {p.nombre} | Stock: {p.stock} | Precio: ${p.p_venta:,.2f}" if p else "❌ No disponible."
    return jsonify({"res": res})


if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(debug=True, port=5001)