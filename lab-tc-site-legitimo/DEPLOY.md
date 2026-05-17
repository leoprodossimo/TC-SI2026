# 🚀 Deploy na AWS EC2

Guia para subir o servidor Flask com Apache reverse proxy (simulação acadêmica MITM) em uma instância EC2.

## Arquitetura

```
Navegador (porta 80) → Apache (mod_proxy) → Flask (127.0.0.1:8080)
```

- **Apache** recebe o tráfego público na porta 80 (parece um site normal)
- **Flask** roda internamente na porta 8080, captura credenciais no SQLite

---

## Pré-requisitos na AWS

1. **Instância EC2** com **Ubuntu 22.04 ou 24.04**
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
scp -i sua-chave.pem -r ./seguranca-simulacao-legitimo ubuntu@<IP-DA-EC2>:~/securebank
```

### 2. Conectar na EC2

```bash
ssh -i sua-chave.pem ubuntu@<IP-DA-EC2>
```

### 3. Executar o deploy

```bash
cd ~/securebank
sudo bash deploy.sh
```

O script faz **tudo automaticamente**:
- Instala Python 3, pip, venv e Apache
- Cria ambiente virtual e instala Flask
- Configura serviço systemd para o Flask
- Configura Apache como reverse proxy (porta 80 → Flask 8080)
- Ativa e inicia ambos os serviços

### 4. Testar

```
http://<IP-PUBLICO-DA-EC2>
```

---

## Comandos Úteis

| Ação | Comando |
|------|---------|
| Status do Flask | `sudo systemctl status securebank` |
| Status do Apache | `sudo systemctl status apache2` |
| Logs do Flask | `sudo journalctl -u securebank -f` |
| Logs do Apache | `sudo tail -f /var/log/apache2/securebank-*.log` |
| Reiniciar tudo | `sudo systemctl restart securebank apache2` |
| Ver credenciais | `sqlite3 /opt/securebank/dados.db "SELECT * FROM logins;"` |

---

## Troubleshooting

### O site não carrega
1. Verifique os serviços: `sudo systemctl status securebank apache2`
2. Verifique o Security Group — porta **80** aberta para **0.0.0.0/0**
3. Veja os logs: `sudo journalctl -u securebank -f`

### Erro "Address already in use" na porta 80
Outro serviço está usando a porta 80:
```bash
sudo lsof -i :80
```

### Atualizar os arquivos do site
```bash
# No terminal local:
scp -i sua-chave.pem -r ./static/* ubuntu@<IP-DA-EC2>:~/securebank/static/
scp -i sua-chave.pem ./server.py ubuntu@<IP-DA-EC2>:~/securebank/

# Na EC2:
sudo cp ~/securebank/server.py /opt/securebank/
sudo cp -r ~/securebank/static/* /opt/securebank/static/
sudo systemctl restart securebank
```
