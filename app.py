from flask import Flask, request, send_from_directory
import os

app = Flask(__name__)

estado = {
    "1ro Primaria": "sin datos",
    "2do Primaria": "sin datos",
    "3ro Primaria": "sin datos",
    "4to Primaria": "sin datos",
    "5to Primaria": "sin datos",
    "6to Primaria": "sin datos",
    "7mo Primaria": "sin datos"
}

@app.route("/")
def home():
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

            /* Header principal con logos */
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

            .institution-logo {
                flex-shrink: 0;
            }

            .institution-logo img {
                height: 100px;
                width: auto;
                filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
                transition: transform 0.3s ease;
            }

            .institution-logo img:hover {
                transform: scale(1.05);
            }

            .dev-logo {
                flex-shrink: 0;
                padding-left: 20px;
                border-left: 2px solid rgba(255,255,255,0.3);
            }

            .dev-logo img {
                height: 65px;
                width: auto;
                opacity: 0.9;
                transition: opacity 0.3s ease;
            }

            .dev-logo img:hover {
                opacity: 1;
            }

            .dev-credit {
                font-size: 0.7rem;
                opacity: 0.6;
                margin-top: 5px;
                text-align: center;
            }

            h1 {
                font-weight: 300;
                letter-spacing: 2px;
                margin: 15px 0 5px 0;
                text-transform: uppercase;
                font-size: 1.8rem;
                color: #e0e0e0;
            }

            .subtitle {
                font-size: 0.9rem;
                opacity: 0.7;
                margin-bottom: 15px;
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

            .stats span {
                margin: 0 5px;
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
                padding: 0 10px;
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
                color: #ffffff;
                box-shadow: 0 8px 20px rgba(0,0,0,0.4);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                border: 1px solid rgba(255,255,255,0.1);
                cursor: pointer;
                -webkit-tap-highlight-color: transparent;
            }

            .card:active {
                transform: scale(0.97);
            }

            .aula-name {
                font-size: 0.85rem;
                opacity: 0.95;
                margin-bottom: 10px;
                letter-spacing: 0.5px;
                font-weight: 600;
                text-align: center;
            }

            .status-text {
                font-size: 1.2rem;
                text-transform: uppercase;
                font-weight: 800;
                letter-spacing: 1px;
            }

            /* Colores de estado */
            .ok { background: linear-gradient(145deg, #28a745, #1e7e34); }
            .falta { background: linear-gradient(145deg, #dc3545, #a71d2a); }
            .sin-datos { background: linear-gradient(145deg, #ffc107, #d39e00); color: #212529; }

            /* Footer */
            .footer {
                margin-top: 30px;
                font-size: 0.7rem;
                opacity: 0.5;
                text-align: center;
                padding: 10px;
            }

            /* Botón flotante para control (solo móvil) */
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
                transition: transform 0.2s;
                border: none;
            }

            .fab:active {
                transform: scale(0.92);
            }

            /* Responsive para móviles */
            @media (max-width: 768px) {
                body {
                    padding: 10px;
                }
                
                .institution-logo img {
                    height: 70px;
                }
                
                .dev-logo img {
                    height: 45px;
                }
                
                .dev-logo {
                    padding-left: 12px;
                }
                
                h1 {
                    font-size: 1.3rem;
                    letter-spacing: 1px;
                }
                
                .subtitle {
                    font-size: 0.75rem;
                }
                
                .container {
                    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                    gap: 12px;
                    padding: 0 5px;
                }
                
                .card {
                    padding: 15px 10px;
                }
                
                .aula-name {
                    font-size: 0.75rem;
                }
                
                .status-text {
                    font-size: 1rem;
                }
                
                .stats {
                    font-size: 0.7rem;
                    padding: 6px 15px;
                    gap: 10px;
                }
                
                .fab {
                    width: 48px;
                    height: 48px;
                    font-size: 20px;
                    bottom: 15px;
                    right: 15px;
                }
            }

            @media (max-width: 480px) {
                .container {
                    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
                    gap: 10px;
                }
                
                .card {
                    padding: 12px 8px;
                }
                
                .aula-name {
                    font-size: 0.7rem;
                }
                
                .status-text {
                    font-size: 0.9rem;
                }
                
                .logo-container {
                    gap: 12px;
                }
                
                .institution-logo img {
                    height: 55px;
                }
                
                .dev-logo img {
                    height: 35px;
                }
            }
        </style>
    </head>
    <body>

    <div class="main-header">
        <div class="logo-container">
            <div class="institution-logo">
                <img src="/static/logo_isae.png" alt="ISAE - Instituto Superior Albert Einstein" onerror="this.style.display='none'">
            </div>
            <div class="dev-logo">
                <img src="/static/logo_cluster.png" alt="ISAE Cluster Tecnológico" onerror="this.style.display='none'">
                <div class="dev-credit">Desarrollo: Cluster Tecnológico</div>
            </div>
        </div>
        <h1>📊 Monitoreo de Aulas</h1>
        <div class="subtitle">Educación Primaria - ISAE</div>
    </div>

    <div class="container" id="aulasContainer">
    """

    # Calculamos estadísticas
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
        // Función rápida para alternar estado (útil en móvil)
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

    if aula in estado:
        estado[aula] = "OK" if valor == "1" else "FALTA"

    return "OK"

@app.route("/control")
def control():
    html = """
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="theme-color" content="#1a3a5c">
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
                transition: transform 0.2s, opacity 0.2s;
                flex: 1;
                min-width: 100px;
                -webkit-tap-highlight-color: transparent;
            }
            button:active {
                transform: scale(0.96);
            }
            .btn-ok {
                background: #28a745;
                color: white;
                box-shadow: 0 4px 15px rgba(40,167,69,0.3);
            }
            .btn-falta {
                background: #dc3545;
                color: white;
                box-shadow: 0 4px 15px rgba(220,53,69,0.3);
            }
            .status-badge {
                text-align: center;
                margin-top: 15px;
                padding: 10px;
                border-radius: 10px;
                font-size: 0.9rem;
                font-weight: bold;
            }
            .footer {
                margin-top: 30px;
                text-align: center;
                font-size: 0.7rem;
                opacity: 0.6;
            }
            @media (max-width: 600px) {
                body { padding: 15px; }
                .logo-bar img { height: 55px; }
                h1 { font-size: 1.2rem; }
                button { padding: 12px 20px; font-size: 0.9rem; }
                .aula-card h3 { font-size: 1rem; }
                .grid { gap: 15px; }
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
            <h1 style="font-size: 1rem; opacity: 0.8;">Primaria ISAE</h1>
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
                <div class="status-badge" id="status-{aula.replace(' ', '-').replace('ro', 'r').replace('mo', 'm')}" style="background: {status_color}; color: {status_text_color}">
                    Estado actual: {current_status}
                </div>
            </div>
        """
    
    html += """
        </div>
        <div class="footer">
            ISAE Cluster Tecnológico - Sistema de Monitoreo | Primaria Completa
        </div>
        <script>
        function updateEstado(aula, estado) {
            const statusId = 'status-' + aula.replace(/ /g, '-').replace('ro', 'r').replace('mo', 'm');
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
                .catch(err => alert('Error al actualizar: ' + err));
        }
        </script>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)