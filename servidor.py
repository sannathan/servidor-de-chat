import socket
import json
from datetime import datetime

# Configurações do servidor

IP_SERVIDOR = '0.0.0.0'
PORTA_SERVIDOR = 3000

BUFFER_SIZE = 1024  # 1024 Bytes

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
        data, addr = server_socket.recvfrom(BUFFER_SIZE) # Recebe até 1024 bytes
        texto = data.decode()

        #Verifica se é comando de entrada ou saída
        if texto.lower().startswith("hi, meu nome eh"):
            nome = texto[16:].strip()

            # Registrar cliente
            clientes[addr] = nome

            print(f"{nome} ({addr}) entrou na sala.")

            # Notificar outros clientes que uma nova pessoa entrou na sala
            mensagem = f"{nome} entrou na sala."
            for cliente in clientes:
                if cliente != addr:
                    server_socket.sendto(mensagem.encode(), cliente)
                continue

        elif texto.lower().startswith("bye"):
            nome = clientes.get(addr, "Desconhecido")

            print(f"{nome} ({addr}) saiu da sala.")

            # Notificar outros clientes
            mensagem = f"{nome} saiu da sala."
            for cliente in clientes:
                if cliente != addr:
                    server_socket.sendto(mensagem.encode(), cliente)
            
            # Remover da lista
            if addr in clientes:
                del clientes[addr]
            continue
        
        # Se não é comando, deve ser pacote JSON de mensagem
        else:
            try:
                pacote = json.loads(texto)

            except:
                print(f"Pacote inválido de {addr}: {texto}")
                continue
            
            # Extrair dados do pacote
            file_id = pacote.get("file_id")
            packet_num = pacote.get("packet_num")
            total_packets = pacote.get("total_packets")
            username = pacote.get("username")
            conteudo_pacote = pacote.get("data")

            if None in [file_id, packet_num, total_packets, username, conteudo_pacote]:
                print(f"Pacote mal formatado de {addr}: {pacote}")
                continue

            #Armazenar os pedaços
            if file_id not in arquivos:
                arquivos[file_id] = {
                    "packets": {},
                    "total": total_packets,
                    "addr": addr,
                    "username": username
                }

            arquivos[file_id]["packets"][packet_num] = conteudo_pacote

            print(f"Recebido pacote {packet_num}/{total_packets} de {username} ({addr})")

        

            # Verificar se o arquivo está completo
            if len(arquivos[file_id]["packets"]) == total_packets: 
                print(f"Arquivo completo de {username} ({addr})")

                # Ordenar pacotes e reconstruir
                conteudo = ''.join(
                    arquivos[file_id]["packets"][i]
                    for i in range(1, total_packets + 1)
                )

                # Gerar timestamp
                ip, porta = addr
                timestamp = datetime.now().strftime('%H:%M:%S %d/%m/%Y')

                # Formatar mensagem
                mensagem_formatada = f"{ip}:{porta}/~{username}: {conteudo} {timestamp}"
                print(mensagem_formatada)

                # Reenviar para todos os outros clientes
                for cliente in clientes:
                    if cliente != addr:
                        server_socket.sendto(mensagem_formatada.encode(), cliente)


                # Limpar estado do arquivo
                del arquivos[file_id]
    except Exception as e:
        print(f"Erro: {e}")
    






