import socket
import json
import zlib
from datetime import datetime

# ========================
# Configurações do servidor
# ========================
IP_SERVIDOR = '0.0.0.0'
PORTA_SERVIDOR = 2000
BUFFER_SIZE = 1024  # 1024 Bytes

# Criando o socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((IP_SERVIDOR, PORTA_SERVIDOR))

print(f"🛰️ Servidor UDP RDT 3.0 esperando conexões na porta {PORTA_SERVIDOR}")

# ========================
# Estruturas de estado
# ========================
clientes = {}        # {(ip, porta): 'nome_usuario'}
arquivos = {}        # {'file_id': {'packets': {}, 'total': int, 'addr': (ip,port), 'username': str}}
ultimo_ack = {}      # {(ip, porta): ultimo_num_seq}

# ========================
# Função para calcular checksum
# ========================
def calcular_checksum(dados: str) -> int:
    return zlib.crc32(dados.encode())

# ========================
# Loop principal do servidor
# ========================
while True:
    try:
        data, addr = server_socket.recvfrom(BUFFER_SIZE)
        texto = data.decode()

        # ========================
        # 1. Comandos de entrada/saída
        # ========================
        if texto.lower().startswith("hi, meu nome eh"):
            nome = texto[16:].strip()
            clientes[addr] = nome
            ultimo_ack[addr] = -1  # Inicializa o controle de ACK

            print(f"[CONECTADO] {nome} ({addr}) entrou na sala.\n")

            # Notificar os outros clientes
            mensagem = f"{nome} entrou na sala.\n"
            for cliente in clientes:
                if cliente != addr:
                    server_socket.sendto(mensagem.encode(), cliente)
            continue

        elif texto.lower().startswith("bye"):
            nome = clientes.get(addr, "Desconhecido")
            print(f"[DESCONECTADO] {nome} ({addr}) saiu da sala.\n")

            # Notificar outros clientes
            mensagem = f"{nome} saiu da sala.\n"
            for cliente in clientes:
                if cliente != addr:
                    server_socket.sendto(mensagem.encode(), cliente)

            # Remover cliente
            clientes.pop(addr, None)
            ultimo_ack.pop(addr, None)
            continue

        # ========================
        # 2. Recebendo pacote de mensagem
        # ========================
        try:
            pacote = json.loads(texto)
        except:
            print(f"[ERRO] Pacote inválido de {addr}: {texto}")
            continue

        # Extração de dados do pacote
        file_id = pacote.get("file_id")
        packet_num = pacote.get("packet_num")
        total_packets = pacote.get("total_packets")
        username = pacote.get("username")
        conteudo_pacote = pacote.get("data")
        checksum = pacote.get("checksum")

        if None in [file_id, packet_num, total_packets, username, conteudo_pacote, checksum]:
            print(f"[ERRO] Pacote mal formatado de {addr}: {pacote}")
            continue

        # ========================
        # 3. Verificação de integridade
        # ========================
        if calcular_checksum(conteudo_pacote) != checksum:
            print(f"[CORRUPÇÃO] Pacote {packet_num} de {username} corrompido. Reenviando último ACK válido ({ultimo_ack[addr]})")
            ack = {"ack_num": ultimo_ack[addr]}
            server_socket.sendto(json.dumps(ack).encode(), addr)
            continue

        # ========================
        # 4. ACK positivo
        # ========================
        ack = {"ack_num": packet_num}
        server_socket.sendto(json.dumps(ack).encode(), addr)
        ultimo_ack[addr] = packet_num
        print(f"[ACK] Enviado ACK para pacote {packet_num} de {username}")

        # ========================
        # 5. Armazenamento do pacote
        # ========================
        if file_id not in arquivos:
            arquivos[file_id] = {
                "packets": {},
                "total": total_packets,
                "addr": addr,
                "username": username
            }

        arquivos[file_id]["packets"][packet_num] = conteudo_pacote
        print(f"[PACOTE] Recebido {packet_num}/{total_packets} de {username} ({addr})")

        # ========================
        # 6. Verificação de completude
        # ========================
        if len(arquivos[file_id]["packets"]) == total_packets:
            print(f"[COMPLETE] Arquivo completo de {username} ({addr})")

            # Reconstituir conteúdo
            conteudo = ''.join(
                arquivos[file_id]["packets"][i]
                for i in range(total_packets)
            )

            # Formatar mensagem final
            ip, porta = addr
            timestamp = datetime.now().strftime('%H:%M:%S %d/%m/%Y')
            mensagem_formatada = f"{ip}:{porta}/~{username}: {conteudo} {timestamp}"
            print(f"[MSG] {mensagem_formatada}")

            # Broadcast para os outros clientes
            for cliente in clientes:
                if cliente != addr:
                    server_socket.sendto(mensagem_formatada.encode(), cliente)

            # Limpar dados do arquivo
            del arquivos[file_id]

    except Exception as e:
        print(f"[ERRO GERAL] {e}")
