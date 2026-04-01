from flask import Blueprint, request, jsonify
from sqlalchemy import func
from docs.models import Repuesto

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    msg  = data.get('msg', '').upper().strip()

    if not msg:
        return jsonify({'res': '❓ Escribe el nombre de un repuesto.'})

    p = Repuesto.query.filter(func.upper(Repuesto.nombre).contains(msg)).first()
    if p:
        estado = '🔴 ¡Stock bajo!' if p.stock < 5 else '🟢 Disponible'
        res = (
            f'📍 <b>{p.nombre}</b><br>'
            f'Stock: {p.stock} uds {estado}<br>'
            f'Precio venta: <b>${p.p_venta:,.2f}</b>'
        )
    else:
        res = f'❌ "{msg}" no encontrado en inventario.'

    return jsonify({'res': res})