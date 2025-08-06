import socket
import json
from datetime import datetime
from protocolrdt3 import is_corrupted, make_ack, extract_data

# Configuração
IP_SERVIDOR = '0.0.0.0'
PORTA_SERVIDOR = 2000
BUFFER_SIZE = 2048

# Estruturas de estado
clientes = {}       # {(ip, porta_envio): {'nome': 'nome_usuario', 'receive_port': porta_recebimento}}
arquivos = {}       # {'file_id': {'packets': {}, 'total': int, 'username': str}}
ultimo_ack = {}     # {(ip, porta): ultimo_num_seq}

# Criar socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((IP_SERVIDOR, PORTA_SERVIDOR))
print(f"🛰️ Servidor RDT 3.0 rodando na porta {PORTA_SERVIDOR}...")

while True:
    try:
        data, addr = server_socket.recvfrom(BUFFER_SIZE)

        # 1️⃣ Verifica corrupção
        if is_corrupted(data):
            print(f"[CORRUPÇÃO] Pacote de {addr}, reenviando ACK último válido {ultimo_ack.get(addr, -1)}")
            ack = make_ack(ultimo_ack.get(addr, -1))
            server_socket.sendto(ack, addr)
            continue

        # 2️⃣ Extrai número de sequência e payload
        seq_num, payload = extract_data(data)
        mensagem_str = payload.decode()

        # 3️⃣ Envia ACK
        ack = make_ack(seq_num)
        server_socket.sendto(ack, addr)
        ultimo_ack[addr] = seq_num
        print(f"[ACK] Enviado ACK {seq_num} para {clientes.get(addr, {}).get('nome', '?')}")

        # 4️⃣ Trata comandos de entrada e saída
        if mensagem_str.lower().startswith("hi, meu nome eh"):
            # Extrai nome e porta de recebimento
            if ":" in mensagem_str:
                nome_parte, receive_port_str = mensagem_str.rsplit(":", 1)
                nome = nome_parte[16:].strip()
                receive_port = int(receive_port_str)
            else:
                nome = mensagem_str[16:].strip()
                receive_port = addr[1]  # Usa mesma porta se não especificada
            
            ip = addr[0]
            receive_addr = (ip, receive_port)
            
            clientes[addr] = {'nome': nome, 'receive_addr': receive_addr}
            ultimo_ack[addr] = -1
            print(f"[CONECTADO] {nome} entrou ({addr}) - recebe em {receive_addr}")

            # Notificar outros
            msg = f"{nome} entrou na sala."
            for cliente_addr, cliente_info in clientes.items():
                if cliente_addr != addr:
                    server_socket.sendto(msg.encode(), cliente_info['receive_addr'])
            continue

        elif mensagem_str.lower() == "bye":
            cliente_info = clientes.get(addr, {})
            nome = cliente_info.get('nome', 'Desconhecido')
            print(f"[DESCONECTADO] {nome} saiu ({addr})")

            # Notificar outros
            msg = f"{nome} saiu da sala."
            for cliente_addr, info in clientes.items():
                if cliente_addr != addr:
                    server_socket.sendto(msg.encode(), info['receive_addr'])

            clientes.pop(addr, None)
            ultimo_ack.pop(addr, None)
            continue

        # 5️⃣ Trata pacote JSON de mensagem/fragmento
        try:
            pacote = json.loads(mensagem_str)
        except json.JSONDecodeError:
            print(f"[ERRO] Mensagem recebida não é JSON válido: {mensagem_str}")
            continue

        file_id = pacote["file_id"]
        total = pacote["total_packets"]
        username = pacote["username"]
        conteudo = pacote["data"]

        if file_id not in arquivos:
            arquivos[file_id] = {"packets": {}, "total": total, "username": username}

        arquivos[file_id]["packets"][pacote["packet_num"]] = conteudo
        print(f"[PACOTE] Recebido {pacote['packet_num']}/{total} de {username}")

        # 6️⃣ Monta a mensagem final se o arquivo estiver completo
        if len(arquivos[file_id]["packets"]) == total:
            mensagem_completa = "".join(
                arquivos[file_id]["packets"][i] for i in range(1, total + 1)
            )
            ip, porta = addr
            timestamp = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            mensagem_formatada = f"{ip}:{porta}/~{username}: {mensagem_completa} {timestamp}"
            print(f"[MSG] {mensagem_formatada}")

            # Enviar para todos
            for cliente_addr, cliente_info in clientes.items():
                if cliente_addr != addr:
                    server_socket.sendto(mensagem_formatada.encode(), cliente_info['receive_addr'])

            del arquivos[file_id]

    except Exception as e:
        print(f"[ERRO] {e}")
