/* ═══════════════════════════════════════════════
   DRIVEFLOW PRO — main.js (MEJORADO)
   ═══════════════════════════════════════════════ */

// ── Tema oscuro / claro ──────────────────────────
const body = document.body;
const savedTheme = localStorage.getItem('df-theme') || 'dark';
body.setAttribute('data-theme', savedTheme);

function toggleTheme() {
    const next = body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    body.setAttribute('data-theme', next);
    localStorage.setItem('df-theme', next);
}

// ── Modal editar ─────────────────────────────────
function abrirEditor(id, nombre, costo, venta, stock) {
    document.getElementById('formEditar').action = `/editar/${id}`;
    document.getElementById('edit_nombre').value = nombre;
    document.getElementById('edit_costo').value  = costo;
    document.getElementById('edit_venta').value  = venta;
    document.getElementById('edit_stock').value  = stock;
    document.getElementById('modalEditar').classList.add('is-open');
    document.getElementById('edit_nombre').focus();
}

function cerrarModal() {
    document.getElementById('modalEditar').classList.remove('is-open');
}

document.getElementById('modalEditar').addEventListener('click', function(e) {
    if (e.target === this) cerrarModal();
});
document.addEventListener('keydown', e => { if (e.key === 'Escape') cerrarModal(); });

// ── Chat ─────────────────────────────────────────
function toggleChat() {
    document.getElementById('chat-ui').classList.toggle('is-open');
    if (document.getElementById('chat-ui').classList.contains('is-open')) {
        document.getElementById('chat-in').focus();
    }
}

async function sendChat() {
    const input = document.getElementById('chat-in');
    const log   = document.getElementById('chat-log');
    const msg   = input.value.trim();
    if (!msg) return;

    const userDiv = document.createElement('div');
    userDiv.className = 'msg-user';
    userDiv.textContent = `Tú: ${msg}`;
    log.appendChild(userDiv);

    input.value = '';
    input.disabled = true;

    try {
        const res  = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ msg })
        });
        const data = await res.json();

        const botDiv = document.createElement('div');
        botDiv.className = 'msg-bot';
        botDiv.innerHTML = `Bot: ${data.res}`;
        log.appendChild(botDiv);
        log.scrollTo({ top: log.scrollHeight, behavior: 'smooth' });
    } catch {
        const errDiv = document.createElement('div');
        errDiv.className = 'msg-bot';
        errDiv.textContent = 'Bot: ❌ Error de conexión.';
        log.appendChild(errDiv);
    } finally {
        input.disabled = false;
        input.focus();
    }
}

// ── Copiar lista de pedido ───────────────────────
async function copiarLista() {
    try {
        const res  = await fetch('/exportar_compras');
        const text = await res.text();
        await navigator.clipboard.writeText(text);
        alert('📋 Lista copiada al portapapeles. ¡Pégala en WhatsApp!');
    } catch {
        alert('❌ No se pudo copiar. Intenta de nuevo.');
    }
}

// ── Auto-hide flash messages ─────────────────────
document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => {
        el.style.transition = 'opacity .5s';
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 500);
    }, 4000);
});

// ── ALERTAS DE STOCK CRÍTICO ─────────────────────
document.querySelectorAll('.row--alert').forEach(row => {
    row.style.animation = 'blink 1s infinite';
});

// ── ANIMACIÓN KPI CARDS ─────────────────────────
document.querySelectorAll('.stat-card strong').forEach(card => {
    card.animate([{ transform: 'scale(1.0)' }, { transform: 'scale(1.1)' }, { transform: 'scale(1.0)' }], {
        duration: 1000,
        iterations: Infinity,
        direction: 'alternate'
    });
});

// ── NOTIFICACIONES DE VENTAS GRANDES ─────────────
document.querySelectorAll('.text-green').forEach(el => {
    if (parseFloat(el.textContent.replace('$','').replace(',','')) > 1000) {
        el.style.backgroundColor = '#28a745';
        el.style.color = '#fff';
        el.style.padding = '2px 6px';
        el.style.borderRadius = '5px';
        el.style.fontWeight = 'bold';
        setTimeout(() => alert('🚀 ¡Venta grande registrada!'), 500);
    }
});

// ── GRÁFICOS DE VENTAS (Chart.js) ───────────────
if (document.getElementById('chartVentas')) {
    const ctx = document.getElementById('chartVentas').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: JSON.parse(document.getElementById('chartVentas').dataset.labels),
            datasets: [{
                label: 'Ventas',
                data: JSON.parse(document.getElementById('chartVentas').dataset.data),
                borderColor: '#007bff',
                backgroundColor: 'rgba(0,123,255,0.2)',
                fill: true
            }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
    });
}

/* ── CSS ANIMATION ── */
const style = document.createElement('style');
style.textContent = `
@keyframes blink {
    0% { background-color: rgba(255,0,0,0.2); }
    50% { background-color: rgba(255,0,0,0.6); }
    100% { background-color: rgba(255,0,0,0.2); }
}`;
document.head.appendChild(style);