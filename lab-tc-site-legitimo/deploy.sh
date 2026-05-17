#!/usr/bin/env bash
set -e

APP_DIR="/opt/securebank"
SERVICE_NAME="securebank"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REAL_USER="${SUDO_USER:-$(whoami)}"

echo "=============================="
echo " DEPLOY SEGURO - SECUREBANK"
echo " (Apache + Flask Reverse Proxy)"
echo "=============================="

# 1. Atualizar pacotes (SEM upgrade)
echo "[1/12] Atualizando pacotes..."
sudo apt update -y

# 2. Instalar dependências do sistema
echo "[2/12] Instalando Python e Apache..."
sudo apt install -y python3 python3-pip python3-venv apache2

# 3. Limpar deploy antigo do Flask
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

# 8. Criar serviço systemd para o Flask
echo "[8/12] Configurando serviço Flask..."
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=SecureBank Flask App (MITM Lab)
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
echo "[9/12] Iniciando serviço Flask..."
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl restart ${SERVICE_NAME}

# 10. Configurar Apache como Reverse Proxy
echo "[10/12] Configurando Apache (reverse proxy)..."
sudo a2enmod proxy proxy_http
sudo a2dissite 000-default 2>/dev/null || true

sudo tee /etc/apache2/sites-available/securebank.conf > /dev/null <<'APACHECONF'
<VirtualHost *:80>
    ServerName localhost

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8080/
    ProxyPassReverse / http://127.0.0.1:8080/

    ErrorLog ${APACHE_LOG_DIR}/securebank-error.log
    CustomLog ${APACHE_LOG_DIR}/securebank-access.log combined
</VirtualHost>
APACHECONF

# 11. Ativar site e reiniciar Apache
echo "[11/12] Ativando site no Apache..."
sudo a2ensite securebank
sudo systemctl restart apache2

# 12. Verificar status dos serviços
echo "[12/12] Status dos serviços:"
echo ""
echo "--- Flask (securebank) ---"
sudo systemctl status ${SERVICE_NAME} --no-pager || true
echo ""
echo "--- Apache ---"
sudo systemctl status apache2 --no-pager || true

echo ""
echo "=============================="
echo " DEPLOY FINALIZADO"
echo "=============================="
echo ""
echo " Arquitetura:"
echo "   Navegador → Apache (:80) → Flask (:8080 local)"
echo ""
echo " Acesse: http://SEU-IP"
echo "=============================="