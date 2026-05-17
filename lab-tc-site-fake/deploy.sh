#!/usr/bin/env bash
# ============================================================
# Simulação acadêmica de ataque MITM (DNS Spoofing)
# Uso exclusivo para fins educacionais em ambiente controlado.
# ============================================================
#
# DEPLOY AUTOMATIZADO — SERVIDOR FAKE
# ====================================
# Este script instala e configura o servidor fake na EC2.
#
# Diferenças do deploy legítimo:
# - Instala em /opt/securebank-fake (em vez de /opt/securebank)
# - Flask roda na porta 8081 (em vez de 8080)
# - Apache faz proxy da porta 80 para Flask 8081
# - Serviço systemd: securebank-fake (em vez de securebank)
#
# Uso:
#   sudo bash deploy.sh
# ============================================================

set -e

APP_DIR="/opt/securebank-fake"
SERVICE_NAME="securebank-fake"
FLASK_PORT=8081
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REAL_USER="${SUDO_USER:-$(whoami)}"

echo "======================================"
echo "  🔴 DEPLOY — SERVIDOR FAKE (MITM)"
echo "  (Apache + Flask Reverse Proxy)"
echo "======================================"

# 1. Atualizar pacotes
echo "[1/12] Atualizando pacotes..."
sudo apt update -y

# 2. Instalar dependências do sistema
echo "[2/12] Instalando Python e Apache..."
sudo apt install -y python3 python3-pip python3-venv apache2

# 3. Limpar deploy antigo
echo "[3/12] Limpando diretório antigo..."
sudo rm -rf "$APP_DIR"
sudo mkdir -p "$APP_DIR"

# 4. Copiar arquivos da aplicação
echo "[4/12] Copiando arquivos..."
sudo cp "$SCRIPT_DIR/server.py" "$APP_DIR/"
sudo cp "$SCRIPT_DIR/requirements.txt" "$APP_DIR/"
sudo cp -r "$SCRIPT_DIR/static" "$APP_DIR/"

# 5. Criar virtualenv
echo "[5/12] Criando ambiente virtual..."
sudo python3 -m venv "$APP_DIR/venv"

# 6. Instalar dependências Python
echo "[6/12] Instalando dependências Python..."
sudo "$APP_DIR/venv/bin/pip" install --upgrade pip
sudo "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

# 7. Ajustar permissões
echo "[7/12] Ajustando permissões..."
sudo chown -R "$REAL_USER:$REAL_USER" "$APP_DIR"

# 8. Criar serviço systemd para o Flask fake
echo "[8/12] Configurando serviço Flask (fake)..."
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=SecureBank FAKE — Simulação MITM (Flask)
After=network.target

[Service]
Type=simple
User=${REAL_USER}
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/venv/bin/python3 ${APP_DIR}/server.py
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# 9. Ativar e iniciar serviço Flask
echo "[9/12] Iniciando serviço Flask (fake)..."
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl restart ${SERVICE_NAME}

# 10. Configurar Apache como Reverse Proxy
echo "[10/12] Configurando Apache (reverse proxy → porta ${FLASK_PORT})..."
sudo a2enmod proxy proxy_http
sudo a2dissite 000-default 2>/dev/null || true

sudo tee /etc/apache2/sites-available/securebank-fake.conf > /dev/null <<APACHECONF
<VirtualHost *:80>
    ServerName localhost

    # Proxy reverso: Apache (porta 80) → Flask (porta ${FLASK_PORT})
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:${FLASK_PORT}/
    ProxyPassReverse / http://127.0.0.1:${FLASK_PORT}/

    ErrorLog \${APACHE_LOG_DIR}/securebank-fake-error.log
    CustomLog \${APACHE_LOG_DIR}/securebank-fake-access.log combined
</VirtualHost>
APACHECONF

# 11. Ativar site e reiniciar Apache
echo "[11/12] Ativando site no Apache..."
sudo a2ensite securebank-fake
sudo systemctl restart apache2

# 12. Verificar status dos serviços
echo "[12/12] Status dos serviços:"
echo ""
echo "--- Flask (${SERVICE_NAME}) ---"
sudo systemctl status ${SERVICE_NAME} --no-pager || true
echo ""
echo "--- Apache ---"
sudo systemctl status apache2 --no-pager || true

echo ""
echo "======================================"
echo "  🔴 DEPLOY FAKE FINALIZADO"
echo "======================================"
echo ""
echo "  Arquitetura:"
echo "    Navegador → Apache (:80) → Flask (:${FLASK_PORT} local)"
echo ""
echo "  Acesse: http://SEU-IP"
echo ""
echo "  ⚠️  Lembre-se de alterar LEGITIMATE_SITE_URL em:"
echo "     - ${APP_DIR}/server.py"
echo "     - ${APP_DIR}/static/script.js"
echo "======================================"
