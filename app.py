from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import sqlite3
import os
from threading import Timer

app = Flask(__name__)

# Base de datos
DATABASE = 'monitoreo.db'

estado = {
    "1ro Primaria": "sin datos",
    "2do Primaria": "sin datos",
    "3ro Primaria": "sin datos",
    "4to Primaria": "sin datos",
    "5to Primaria": "sin datos",
    "6to Primaria": "sin datos",
    "7mo Primaria": "sin datos"
}

def init_db():
    """Inicializar la base de datos"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS historial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aula TEXT NOT NULL,
        estado_anterior TEXT NOT NULL,
        estado_nuevo TEXT NOT NULL,
        fecha TIMESTAMP NOT NULL,
        ip TEXT
    )''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_fecha ON historial(fecha)')
    conn.commit()
    conn.close()

def limpiar_registros_antiguos():
    """Eliminar registros de más de 7 días"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    fecha_limite = datetime.now() - timedelta(days=7)
    c.execute("DELETE FROM historial WHERE fecha < ?", (fecha_limite,))
    eliminados = c.rowcount
    conn.commit()
    conn.close()
    if eliminados > 0:
        print(f"✅ Limpieza automática: {eliminados} registros antiguos eliminados")

def registrar_cambio(aula, estado_anterior, estado_nuevo, ip="0.0.0.0"):
    """Registrar un cambio en la base de datos"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''INSERT INTO historial (aula, estado_anterior, estado_nuevo, fecha, ip) 
                 VALUES (?, ?, ?, ?, ?)''',
              (aula, estado_anterior, estado_nuevo, datetime.now(), ip))
    conn.commit()
    conn.close()
    
    # Limpiar registros antiguos cada 10 cambios
    if c.lastrowid % 10 == 0:
        limpiar_registros_antiguos()

def obtener_estadisticas():
    """Obtener estadísticas del historial"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Total de cambios en las últimas 24 horas
    hace_24h = datetime.now() - timedelta(hours=24)
    c.execute("SELECT COUNT(*) FROM historial WHERE fecha > ?", (hace_24h,))
    cambios_24h = c.fetchone()[0]
    
    # Cambios por aula
    c.execute('''SELECT aula, COUNT(*) as total 
                 FROM historial 
                 WHERE fecha > datetime('now', '-7 days')
                 GROUP BY aula 
                 ORDER BY total DESC''')
    cambios_por_aula = c.fetchall()
    
    # Último cambio
    c.execute('''SELECT aula, estado_nuevo, fecha 
                 FROM historial 
                 ORDER BY fecha DESC LIMIT 1''')
    ultimo_cambio = c.fetchone()
    
    conn.close()
    
    return {
        'cambios_24h': cambios_24h,
        'cambios_por_aula': cambios_por_aula,
        'ultimo_cambio': ultimo_cambio
    }

@app.route("/")
def home():
    # Limpiar registros al iniciar
    limpiar_registros_antiguos()
    
    html = """
    <html>
    <head>
        <meta http-equiv="refresh" content="2">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="theme-color" content="#1a3a5c">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                -webkit-tap-highlight-color: transparent;
            }

            body {
                font-family: -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background: radial-gradient(circle at top, #1a3a5c, #0a1a2e);
                color: #ffffff;
                margin: 0;
                padding: 15px;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }

            .main-header {
                text-align: center;
                margin-bottom: 25px;
                width: 100%;
            }

            .logo-container {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 20px;
                flex-wrap: wrap;
                margin-bottom: 15px;
            }

            .institution-logo img {
                height: 100px;
                width: auto;
                filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
                transition: transform 0.3s ease;
            }

            .dev-logo img {
                height: 65px;
                width: auto;
                opacity: 0.9;
                transition: opacity 0.3s ease;
            }

            .dev-logo {
                padding-left: 20px;
                border-left: 2px solid rgba(255,255,255,0.3);
            }

            .dev-credit {
                font-size: 0.7rem;
                opacity: 0.6;
                margin-top: 5px;
            }

            h1 {
                font-weight: 300;
                letter-spacing: 2px;
                margin: 15px 0 5px 0;
                font-size: 1.8rem;
            }

            .subtitle {
                font-size: 0.9rem;
                opacity: 0.7;
                margin-bottom: 15px;
            }

            .nav-buttons {
                display: flex;
                gap: 15px;
                justify-content: center;
                margin-bottom: 20px;
            }

            .nav-btn {
                padding: 10px 20px;
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 25px;
                color: white;
                text-decoration: none;
                font-size: 0.9rem;
                transition: all 0.3s;
            }

            .nav-btn.active {
                background: #007bff;
                border-color: #007bff;
            }

            .stats {
                display: inline-flex;
                gap: 20px;
                background: rgba(0,0,0,0.3);
                padding: 8px 20px;
                border-radius: 50px;
                margin-bottom: 20px;
                font-size: 0.8rem;
                flex-wrap: wrap;
                justify-content: center;
            }

            .ok-count { color: #28a745; font-weight: bold; }
            .falta-count { color: #dc3545; font-weight: bold; }
            .total-count { color: #ffc107; font-weight: bold; }

            .container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
                gap: 15px;
                width: 100%;
                max-width: 1200px;
                margin: 10px auto;
            }

            .card {
                padding: 20px 12px;
                border-radius: 20px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                font-size: 16px;
                font-weight: bold;
                box-shadow: 0 8px 20px rgba(0,0,0,0.4);
                transition: transform 0.2s ease;
                border: 1px solid rgba(255,255,255,0.1);
                cursor: pointer;
            }

            .card:active {
                transform: scale(0.97);
            }

            .aula-name {
                font-size: 0.85rem;
                opacity: 0.95;
                margin-bottom: 10px;
                font-weight: 600;
                text-align: center;
            }

            .status-text {
                font-size: 1.2rem;
                text-transform: uppercase;
                font-weight: 800;
            }

            .ok { background: linear-gradient(145deg, #28a745, #1e7e34); }
            .falta { background: linear-gradient(145deg, #dc3545, #a71d2a); }
            .sin-datos { background: linear-gradient(145deg, #ffc107, #d39e00); color: #212529; }

            .footer {
                margin-top: 30px;
                font-size: 0.7rem;
                opacity: 0.5;
                text-align: center;
            }

            .fab {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: linear-gradient(145deg, #007bff, #0056b3);
                color: white;
                width: 56px;
                height: 56px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                cursor: pointer;
                font-size: 24px;
                text-decoration: none;
                z-index: 1000;
            }

            @media (max-width: 768px) {
                .institution-logo img { height: 70px; }
                .dev-logo img { height: 45px; }
                h1 { font-size: 1.3rem; }
                .container { grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); }
            }
        </style>
    </head>
    <body>

    <div class="main-header">
        <div class="logo-container">
            <div class="institution-logo">
                <img src="/static/logo_isae.png" alt="ISAE" onerror="this.style.display='none'">
            </div>
            <div class="dev-logo">
                <img src="/static/logo_cluster.png" alt="Cluster" onerror="this.style.display='none'">
                <div class="dev-credit">Desarrollo: Cluster Tecnológico</div>
            </div>
        </div>
        <h1>📊 Monitoreo de Aulas</h1>
        <div class="subtitle">Educación Primaria - ISAE</div>
        
        <div class="nav-buttons">
            <a href="/" class="nav-btn active">📺 Monitoreo</a>
            <a href="/historial" class="nav-btn">📜 Historial</a>
            <a href="/estadisticas" class="nav-btn">📈 Estadísticas</a>
        </div>
    </div>

    <div class="container">
    """

    # Calcular estadísticas
    ok_count = sum(1 for v in estado.values() if v.upper() == "OK")
    falta_count = sum(1 for v in estado.values() if v.upper() == "FALTA")
    total = len(estado)
    
    html += f"""
        <div class="stats">
            <span>✅ <span class="ok-count">{ok_count}</span></span>
            <span>❌ <span class="falta-count">{falta_count}</span></span>
            <span>📊 Total: <span class="total-count">{total}</span></span>
        </div>
    """

    for aula in estado:
        val = estado[aula].upper()
        if val == "OK":
            clase = "ok"
        elif val == "SIN DATOS":
            clase = "sin-datos"
        else:
            clase = "falta"
            
        html += f"""
        <div class="card {clase}" onclick="toggleStatus('{aula}')">
            <div class="aula-name">{aula.upper()}</div>
            <div class="status-text">{val}</div>
        </div>
        """

    html += """
    </div>
    <div class="footer">
        ISAE - Instituto Superior Albert Einstein | Monitoreo en tiempo real
    </div>
    
    <a href="/control" class="fab" title="Panel de Control">🎮</a>
    
    <script>
    function toggleStatus(aula) {
        let currentStatus = event.target.closest('.card').querySelector('.status-text').innerText;
        let newStatus = (currentStatus === 'OK') ? 0 : 1;
        fetch(`/update?aula=${encodeURIComponent(aula)}&estado=${newStatus}`)
            .then(() => location.reload())
            .catch(err => alert('Error: ' + err));
    }
    </script>
    </body>
    </html>
    """
    return html

@app.route("/update")
def update():
    aula = request.args.get("aula")
    valor = request.args.get("estado")
    ip = request.remote_addr

    if aula in estado:
        estado_anterior = estado[aula]
        estado_nuevo = "OK" if valor == "1" else "FALTA"
        
        # Solo registrar si realmente hubo cambio
        if estado_anterior != estado_nuevo:
            estado[aula] = estado_nuevo
            registrar_cambio(aula, estado_anterior, estado_nuevo, ip)
            
            # Limpiar registros antiguos después de cada cambio
            limpiar_registros_antiguos()

    return "OK"

@app.route("/control")
def control():
    html = """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #1a3a5c, #0a1a2e);
                color: white;
                padding: 20px;
                min-height: 100vh;
            }
            .header {
                text-align: center;
                margin-bottom: 25px;
            }
            .logo-bar {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 20px;
                margin-bottom: 15px;
                flex-wrap: wrap;
            }
            .logo-bar img {
                height: 80px;
            }
            h1 {
                font-size: 1.5rem;
                font-weight: 300;
                margin: 10px 0;
            }
            .back-link {
                display: inline-block;
                margin-top: 10px;
                color: #ffc107;
                text-decoration: none;
                font-size: 0.9rem;
            }
            .nav-buttons {
                display: flex;
                gap: 10px;
                justify-content: center;
                margin: 15px 0;
            }
            .nav-btn {
                padding: 8px 16px;
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 20px;
                color: white;
                text-decoration: none;
                font-size: 0.85rem;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                max-width: 1200px;
                margin: 0 auto;
            }
            .aula-card {
                background: rgba(255,255,255,0.1);
                border-radius: 18px;
                padding: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
            }
            .aula-card h3 {
                margin-bottom: 15px;
                font-size: 1.2rem;
                text-align: center;
            }
            .buttons {
                display: flex;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
            }
            button {
                padding: 14px 28px;
                font-size: 1rem;
                font-weight: bold;
                border: none;
                border-radius: 12px;
                cursor: pointer;
                transition: transform 0.2s;
                flex: 1;
                min-width: 100px;
            }
            button:active {
                transform: scale(0.96);
            }
            .btn-ok {
                background: #28a745;
                color: white;
            }
            .btn-falta {
                background: #dc3545;
                color: white;
            }
            .status-badge {
                text-align: center;
                margin-top: 15px;
                padding: 10px;
                border-radius: 10px;
                font-size: 0.9rem;
                font-weight: bold;
            }
            @media (max-width: 600px) {
                .logo-bar img { height: 55px; }
                h1 { font-size: 1.2rem; }
                button { padding: 12px 20px; }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo-bar">
                <img src="/static/logo_isae.png" alt="ISAE" onerror="this.style.display='none'">
                <img src="/static/logo_cluster.png" alt="Cluster" onerror="this.style.display='none'">
            </div>
            <h1>🎮 Panel de Control</h1>
            <div class="nav-buttons">
                <a href="/" class="nav-btn">📺 Monitoreo</a>
                <a href="/historial" class="nav-btn">📜 Historial</a>
                <a href="/estadisticas" class="nav-btn">📈 Estadísticas</a>
            </div>
            <a href="/" class="back-link">← Volver al Monitoreo</a>
        </div>
        <div class="grid">
    """
    
    for aula in estado:
        current_status = estado[aula].upper()
        status_color = "#28a745" if current_status == "OK" else "#dc3545" if current_status == "FALTA" else "#ffc107"
        status_text_color = "#000" if current_status == "SIN DATOS" else "#fff"
        
        html += f"""
            <div class="aula-card">
                <h3>📚 {aula.upper()}</h3>
                <div class="buttons">
                    <button class="btn-ok" onclick="updateEstado('{aula}', 1)">✅ OK (1)</button>
                    <button class="btn-falta" onclick="updateEstado('{aula}', 0)">❌ FALTA (0)</button>
                </div>
                <div class="status-badge" id="status-{aula.replace(' ', '-')}" style="background: {status_color}; color: {status_text_color}">
                    Estado actual: {current_status}
                </div>
            </div>
        """
    
    html += """
        </div>
        <script>
        function updateEstado(aula, estado) {
            const statusId = 'status-' + aula.replace(/ /g, '-');
            fetch(`/update?aula=${encodeURIComponent(aula)}&estado=${estado}`)
                .then(() => {
                    const statusDiv = document.getElementById(statusId);
                    const newStatus = estado === 1 ? 'OK' : 'FALTA';
                    statusDiv.textContent = `Estado actual: ${newStatus}`;
                    if (estado === 1) {
                        statusDiv.style.background = '#28a745';
                        statusDiv.style.color = 'white';
                    } else {
                        statusDiv.style.background = '#dc3545';
                        statusDiv.style.color = 'white';
                    }
                })
                .catch(err => alert('Error: ' + err));
        }
        </script>
    </body>
    </html>
    """
    return html

@app.route("/historial")
def historial():
    """Página para ver el historial de cambios"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Obtener parámetros de paginación
    pagina = int(request.args.get('pagina', 1))
    por_pagina = 20
    offset = (pagina - 1) * por_pagina
    
    # Verificar si hay auto-refresco (por defecto 10 segundos)
    auto_refresh = request.args.get('refresh', '10')
    
    # Contar total de registros
    c.execute("SELECT COUNT(*) FROM historial")
    total_registros = c.fetchone()[0]
    
    # Obtener registros con paginación
    c.execute('''SELECT id, aula, estado_anterior, estado_nuevo, fecha, ip 
                 FROM historial 
                 ORDER BY fecha DESC 
                 LIMIT ? OFFSET ?''', (por_pagina, offset))
    registros = c.fetchall()
    
    conn.close()
    
    total_paginas = (total_registros + por_pagina - 1) // por_pagina
    
    html = f"""
    <html>
    <head>
        <meta http-equiv="refresh" content="{auto_refresh}">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #1a3a5c, #0a1a2e);
                color: white;
                padding: 20px;
                min-height: 100vh;
            }}
            .header {{
                text-align: center;
                margin-bottom: 25px;
            }}
            .logo-bar {{
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 20px;
                margin-bottom: 15px;
                flex-wrap: wrap;
            }}
            .logo-bar img {{
                height: 80px;
            }}
            h1 {{
                font-size: 1.5rem;
                font-weight: 300;
            }}
            .nav-buttons {{
                display: flex;
                gap: 10px;
                justify-content: center;
                margin: 15px 0;
                flex-wrap: wrap;
            }}
            .nav-btn {{
                padding: 8px 16px;
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 20px;
                color: white;
                text-decoration: none;
                font-size: 0.85rem;
                transition: all 0.3s;
            }}
            .nav-btn:hover {{
                background: rgba(255,255,255,0.2);
            }}
            .back-link {{
                display: inline-block;
                margin-top: 10px;
                color: #ffc107;
                text-decoration: none;
            }}
            .stats-info {{
                background: rgba(0,0,0,0.3);
                padding: 10px;
                border-radius: 10px;
                margin: 15px auto;
                max-width: 400px;
                text-align: center;
            }}
            .refresh-control {{
                background: rgba(0,0,0,0.3);
                padding: 10px;
                border-radius: 10px;
                margin: 15px auto;
                max-width: 300px;
                text-align: center;
                display: flex;
                gap: 10px;
                justify-content: center;
                align-items: center;
                flex-wrap: wrap;
            }}
            .refresh-btn {{
                padding: 5px 12px;
                background: #007bff;
                border: none;
                border-radius: 15px;
                color: white;
                cursor: pointer;
                font-size: 0.8rem;
                transition: all 0.3s;
            }}
            .refresh-btn:hover {{
                background: #0056b3;
            }}
            .refresh-indicator {{
                font-size: 0.8rem;
                color: #ffc107;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: rgba(255,255,255,0.05);
                border-radius: 15px;
                overflow: hidden;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }}
            th {{
                background: rgba(0,0,0,0.3);
                font-weight: 600;
            }}
            .cambio-ok {{
                color: #28a745;
                font-weight: bold;
            }}
            .cambio-falta {{
                color: #dc3545;
                font-weight: bold;
            }}
            .pagination {{
                display: flex;
                justify-content: center;
                gap: 10px;
                margin: 20px 0;
                flex-wrap: wrap;
            }}
            .page-link {{
                padding: 8px 15px;
                background: rgba(255,255,255,0.1);
                border-radius: 8px;
                text-decoration: none;
                color: white;
                transition: background 0.3s;
            }}
            .page-link:hover {{
                background: rgba(255,255,255,0.2);
            }}
            .page-link.active {{
                background: #007bff;
            }}
            .export-btn {{
                display: inline-block;
                padding: 10px 20px;
                background: #28a745;
                color: white;
                text-decoration: none;
                border-radius: 25px;
                margin: 10px;
                transition: all 0.3s;
            }}
            .export-btn:hover {{
                background: #1e7e34;
                transform: scale(1.05);
            }}
            @media (max-width: 768px) {{
                th, td {{ padding: 8px; font-size: 0.7rem; }}
                .logo-bar img {{ height: 55px; }}
                h1 {{ font-size: 1.2rem; }}
                .nav-btn {{ font-size: 0.7rem; padding: 6px 12px; }}
            }}
        </style>
        <script>
            function changeRefresh(seconds) {{
                window.location.href = `/historial?refresh=${{seconds}}&pagina={pagina}`;
            }}
            
            function stopRefresh() {{
                window.location.href = `/historial?refresh=0&pagina={pagina}`;
            }}
            
            // Mostrar cuenta regresiva para el refresco
            let refreshTime = {auto_refresh};
            if (refreshTime > 0) {{
                setInterval(function() {{
                    if (refreshTime > 0) {{
                        refreshTime--;
                        const indicator = document.getElementById('countdown');
                        if (indicator) indicator.textContent = `Actualizando en ${{refreshTime}}s`;
                    }}
                }}, 1000);
            }}
        </script>
    </head>
    <body>
        <div class="header">
            <div class="logo-bar">
                <img src="/static/logo_isae.png" alt="ISAE" onerror="this.style.display='none'">
                <img src="/static/logo_cluster.png" alt="Cluster" onerror="this.style.display='none'">
            </div>
            <h1>📜 Historial de Cambios</h1>
            <div class="nav-buttons">
                <a href="/" class="nav-btn">📺 Monitoreo</a>
                <a href="/control" class="nav-btn">🎮 Control</a>
                <a href="/estadisticas" class="nav-btn">📈 Estadísticas</a>
                <a href="/exportar-csv" class="nav-btn" style="background: #17a2b8;">📄 Exportar CSV</a>
            </div>
            <a href="/" class="back-link">← Volver al Monitoreo</a>
        </div>
        
        <div class="stats-info">
            Total de registros: {total_registros} (últimos 7 días)
        </div>
        
        <div class="refresh-control">
            <span>🔄 Auto-refresco:</span>
            <button class="refresh-btn" onclick="changeRefresh(5)">5s</button>
            <button class="refresh-btn" onclick="changeRefresh(10)">10s</button>
            <button class="refresh-btn" onclick="changeRefresh(30)">30s</button>
            <button class="refresh-btn" onclick="changeRefresh(60)">60s</button>
            <button class="refresh-btn" onclick="stopRefresh()">⏸️ Pausar</button>
            <span class="refresh-indicator" id="countdown">
                {f"Actualizando en {auto_refresh}s" if auto_refresh != '0' else "Auto-refresco pausado"}
            </span>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Aula</th>
                    <th>Cambio</th>
                    <th>Fecha y Hora</th>
                    <th>IP</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for registro in registros:
        cambio_clase = "cambio-ok" if registro[3] == "OK" else "cambio-falta"
        fecha = datetime.strptime(registro[4], '%Y-%m-%d %H:%M:%S.%f').strftime('%d/%m/%Y %H:%M:%S')
        html += f"""
            <tr>
                <td>{registro[0]}</td>
                <td>{registro[1]}</td>
                <td class="{cambio_clase}">{registro[2]} → {registro[3]}</td>
                <td>{fecha}</td>
                <td>{registro[5]}</td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>
        
        <div class="pagination">
    """
    
    # Mostrar solo un rango de páginas para no saturar
    rango = 5
    inicio = max(1, pagina - rango)
    fin = min(total_paginas, pagina + rango)
    
    if inicio > 1:
        html += f'<a href="/historial?refresh={auto_refresh}&pagina=1" class="page-link">1...</a>'
    
    for i in range(inicio, fin + 1):
        active = "active" if i == pagina else ""
        html += f'<a href="/historial?refresh={auto_refresh}&pagina={i}" class="page-link {active}">{i}</a>'
    
    if fin < total_paginas:
        html += f'<a href="/historial?refresh={auto_refresh}&pagina={total_paginas}" class="page-link">...{total_paginas}</a>'
    
    html += f"""
        </div>
        <div class="stats-info">
            Página {pagina} de {total_paginas} | Mostrando {len(registros)} registros
        </div>
        
        <div style="text-align: center; margin-top: 20px;">
            <a href="/exportar-excel" class="export-btn">📥 Exportar a Excel (CSV)</a>
        </div>
        
        <div style="text-align: center; margin-top: 20px; font-size: 0.7rem; opacity: 0.5;">
            Los registros se mantienen por 7 días automáticamente
        </div>
    </body>
    </html>
    """
    
    return html

@app.route("/estadisticas")
def estadisticas():
    """Página de estadísticas"""
    stats = obtener_estadisticas()
    
    html = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #1a3a5c, #0a1a2e);
                color: white;
                padding: 20px;
                min-height: 100vh;
            }}
            .header {{
                text-align: center;
                margin-bottom: 25px;
            }}
            .logo-bar {{
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 20px;
                margin-bottom: 15px;
                flex-wrap: wrap;
            }}
            .logo-bar img {{
                height: 80px;
            }}
            h1 {{
                font-size: 1.5rem;
                font-weight: 300;
            }}
            .nav-buttons {{
                display: flex;
                gap: 10px;
                justify-content: center;
                margin: 15px 0;
            }}
            .nav-btn {{
                padding: 8px 16px;
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 20px;
                color: white;
                text-decoration: none;
                font-size: 0.85rem;
            }}
            .back-link {{
                display: inline-block;
                margin-top: 10px;
                color: #ffc107;
                text-decoration: none;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                max-width: 1200px;
                margin: 20px auto;
            }}
            .stat-card {{
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 20px;
                backdrop-filter: blur(10px);
            }}
            .stat-card h3 {{
                margin-bottom: 15px;
                font-size: 1.2rem;
                border-bottom: 2px solid rgba(255,255,255,0.3);
                padding-bottom: 8px;
            }}
            .big-number {{
                font-size: 3rem;
                font-weight: bold;
                text-align: center;
                margin: 20px 0;
                color: #ffc107;
            }}
            .aula-list {{
                list-style: none;
            }}
            .aula-list li {{
                padding: 10px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                display: flex;
                justify-content: space-between;
            }}
            .aula-name {{
                font-weight: bold;
            }}
            .cambio-count {{
                color: #28a745;
                font-weight: bold;
            }}
            .last-change {{
                text-align: center;
                margin-top: 20px;
                padding: 15px;
                background: rgba(0,0,0,0.3);
                border-radius: 10px;
            }}
            @media (max-width: 768px) {{
                .logo-bar img {{ height: 55px; }}
                .big-number {{ font-size: 2rem; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo-bar">
                <img src="/static/logo_isae.png" alt="ISAE" onerror="this.style.display='none'">
                <img src="/static/logo_cluster.png" alt="Cluster" onerror="this.style.display='none'">
            </div>
            <h1>📈 Estadísticas del Sistema</h1>
            <div class="nav-buttons">
                <a href="/" class="nav-btn">📺 Monitoreo</a>
                <a href="/control" class="nav-btn">🎮 Control</a>
                <a href="/historial" class="nav-btn">📜 Historial</a>
            </div>
            <a href="/" class="back-link">← Volver al Monitoreo</a>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>📊 Cambios recientes</h3>
                <div class="big-number">{stats['cambios_24h']}</div>
                <p style="text-align: center;">cambios en las últimas 24 horas</p>
            </div>
            
            <div class="stat-card">
                <h3>🏆 Aulas más activas</h3>
                <ul class="aula-list">
    """
    
    for aula, total in stats['cambios_por_aula'][:5]:
        html += f"""
                    <li>
                        <span class="aula-name">{aula}</span>
                        <span class="cambio-count">{total} cambios</span>
                    </li>
        """
    
    html += """
                </ul>
            </div>
        </div>
        
        <div class="last-change">
            <strong>🕐 Último cambio registrado</strong><br>
    """
    
    if stats['ultimo_cambio']:
        aula, estado, fecha = stats['ultimo_cambio']
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S.%f')
        fecha_formateada = fecha_obj.strftime('%d/%m/%Y %H:%M:%S')
        html += f"""
            {aula} → {estado}<br>
            {fecha_formateada}
        """
    else:
        html += "No hay cambios registrados aún"
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html

@app.route("/exportar-csv")
def exportar_csv():
    """Exportar historial a CSV con separador correcto"""
    import csv
    from io import StringIO
    from flask import Response
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''SELECT id, aula, estado_anterior, estado_nuevo, fecha, ip 
                 FROM historial 
                 ORDER BY fecha DESC''')
    registros = c.fetchall()
    conn.close()
    
    # Crear CSV con separador punto y coma (mejor para Excel español)
    output = StringIO()
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    
    # Escribir encabezados
    writer.writerow(['ID', 'Aula', 'Estado Anterior', 'Estado Nuevo', 'Fecha y Hora', 'IP'])
    
    # Escribir datos
    for registro in registros:
        fecha = datetime.strptime(registro[4], '%Y-%m-%d %H:%M:%S.%f').strftime('%d/%m/%Y %H:%M:%S')
        writer.writerow([registro[0], registro[1], registro[2], registro[3], fecha, registro[5]])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=historial_isae_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )
@app.route("/borrar-hasta")
def borrar_hasta():
    """Borrar registros hasta una fecha específica"""
    fecha = request.args.get("fecha")  # formato: 2026-04-20
    
    if not fecha:
        return "Usar: /borrar-hasta?fecha=2026-04-20"
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM historial WHERE DATE(fecha) <= ?", (fecha,))
    eliminados = c.rowcount
    conn.commit()
    conn.close()
    
    return f"✅ Borrados {eliminados} registros hasta {fecha}"

# Inicializar base de datos
init_db()
limpiar_registros_antiguos()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)