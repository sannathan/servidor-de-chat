import socket
import json
from datetime import datetime

# Configurações do servidor

IP_SERVIDOR = '0.0.0.0'
PORTA_SERVIDOR = 3000

BUFFER_SIZE = 2048

# Criando o socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Associando o IP e porta
server_socket.bind((IP_SERVIDOR, PORTA_SERVIDOR)) # Porta do servidor
print(f"🛰️ Servidor UDP esperando conexões na porta {PORTA_SERVIDOR}")

# Estruturas para armazenar estado
clientes = {}  # {'(ip, porta)': 'nome_usuario'}
arquivos = {}  # {'file_id': {'packets': {}, 'total': int, 'addr': (ip,port), 'username': str}}

while True:
    
    try:
        data, addr = server_socket.recvfrom(BUFFER_SIZE) # Recebe até 2048 bytes
        pacote = json.loads(data.decode())

        texto = data.decode()
    except:
        print(f"Pacote inválido de {addr}")
        continue

    file_id = pacote["file_id"]
    packet_num = pacote["packet_num"]
    total_packets = pacote["total_packets"]
    username = pacote["username"]
    texto = pacote["data"]

    # Salvar cliente
    clientes.add(addr)

    # Inicializar estado do arquivo se necessário
    if file_id not in arquivos:
        arquivos[file_id] = {
            "packets": {},
            "total": total_packets,
            "addr": addr,
            "username": username
        }
    
    arquivos[file_id]["packets"][packet_num] = texto

    # Verificar se o arquivo está completo
    if len(arquivos[file_id]["packets"]) == total_packets: 
        print(f"Arquivo completo de {username} ({addr})")

        # Ordenar pacotes e reconstruir
        conteudo = ''.join(
            arquivos[file_id]["packets"][i]
            for i in range(1, total_packets + 1)
        )

        ip, porta = addr
        timestamp = datetime.now().strftime('%H:%M:%S %d/%m/%Y')
        mensagem_formatada = f"{ip}:{porta}/~{username}: {conteudo} {timestamp}"

        print(mensagem_formatada)

        # Reenviar para todos os outros clientes
        for cliente in clientes:
            if cliente != addr:
                server_socket.sendto(mensagem_formatada.encode(), cliente)


        # Limpar estado do arquivo
        del arquivos[file_id]
    






