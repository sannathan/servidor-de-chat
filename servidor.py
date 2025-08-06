import socket
import json
from datetime import datetime
from protocolrdt3 import is_corrupted, make_ack, extract_data

# ===== CONFIGURAÇÕES DO SERVIDOR =====
IP_SERVIDOR = '0.0.0.0'    # Escuta em todas as interfaces de rede
PORTA_SERVIDOR = 2000       # Porta onde o servidor irá escutar
BUFFER_SIZE = 2048          # Tamanho máximo do buffer para recebimento

# ===== ESTRUTURAS DE DADOS GLOBAIS =====
# Dicionário de clientes conectados
# Formato: {(ip, porta_envio): {'nome': 'nome_usuario', 'receive_addr': (ip, porta_recebimento)}}
clientes = {}

# Dicionário para armazenar arquivos sendo recebidos em fragmentos
# Formato: {'file_id': {'packets': {num_pacote: conteudo}, 'total': total_pacotes, 'username': 'nome'}}
arquivos = {}

# Controle de números de sequência do protocolo RDT3 para cada cliente
# Formato: {(ip, porta): ultimo_num_seq_confirmado}
ultimo_ack = {}

# ===== INICIALIZAÇÃO DO SERVIDOR =====
# Criar socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((IP_SERVIDOR, PORTA_SERVIDOR))
print(f"🛰️ Servidor RDT 3.0 rodando na porta {PORTA_SERVIDOR}...")

# ===== LOOP PRINCIPAL DO SERVIDOR =====
while True:
    try:
        # Recebe dados de qualquer cliente
        data, addr = server_socket.recvfrom(BUFFER_SIZE)

        # ===== ETAPA 1: VERIFICAÇÃO DE CORRUPÇÃO =====
        if is_corrupted(data):
            print(f"[CORRUPÇÃO] Pacote de {addr}, reenviando ACK último válido {ultimo_ack.get(addr, -1)}")
            # Reenvia o último ACK válido
            ack = make_ack(ultimo_ack.get(addr, -1))
            server_socket.sendto(ack, addr)
            continue

        # ===== ETAPA 2: EXTRAÇÃO DOS DADOS =====
        seq_num, payload = extract_data(data)
        mensagem_str = payload.decode()

        # ===== ETAPA 3: ENVIO DE ACK =====
        ack = make_ack(seq_num)
        server_socket.sendto(ack, addr)
        ultimo_ack[addr] = seq_num
        print(f"[ACK] Enviado ACK {seq_num} para {clientes.get(addr, {}).get('nome', '?')}")

        # ===== ETAPA 4: TRATAMENTO DE COMANDOS =====
        
        # === COMANDO DE ENTRADA ===
        if mensagem_str.lower().startswith("hi, meu nome eh"):
            # Extrai nome e porta de recebimento do comando
            if ":" in mensagem_str:
                nome_parte, receive_port_str = mensagem_str.rsplit(":", 1)
                nome = nome_parte[16:].strip()  # Remove "hi, meu nome eh "
                receive_port = int(receive_port_str)
            else:
                # Fallback: usa mesma porta se não especificada
                nome = mensagem_str[16:].strip()
                receive_port = addr[1]
            
            ip = addr[0]
            receive_addr = (ip, receive_port)
            
            # Registra cliente com suas informações
            clientes[addr] = {'nome': nome, 'receive_addr': receive_addr}
            ultimo_ack[addr] = -1  # Reseta controle de sequência
            print(f"[CONECTADO] {nome} entrou ({addr}) - recebe em {receive_addr}")

            # Notifica outros clientes sobre a entrada
            msg = f"{nome} entrou na sala."
            for cliente_addr, cliente_info in clientes.items():
                if cliente_addr != addr:  # Não envia para quem entrou
                    server_socket.sendto(msg.encode(), cliente_info['receive_addr'])
            continue

        # === COMANDO DE SAÍDA ===
        elif mensagem_str.lower() == "bye":
            cliente_info = clientes.get(addr, {})
            nome = cliente_info.get('nome', 'Desconhecido')
            print(f"[DESCONECTADO] {nome} saiu ({addr})")

            # Notifica outros clientes sobre a saída
            msg = f"{nome} saiu da sala."
            for cliente_addr, info in clientes.items():
                if cliente_addr != addr:  # Não envia para quem saiu
                    server_socket.sendto(msg.encode(), info['receive_addr'])

            # Remove cliente das estruturas de dados
            clientes.pop(addr, None)
            ultimo_ack.pop(addr, None)
            continue

        # ===== ETAPA 5: TRATAMENTO DE MENSAGENS/FRAGMENTOS =====
        try:
            # Tenta fazer parse do JSON da mensagem
            pacote = json.loads(mensagem_str)
        except json.JSONDecodeError:
            print(f"[ERRO] Mensagem recebida não é JSON válido: {mensagem_str}")
            continue

        # Extrai informações do pacote JSON
        file_id = pacote["file_id"]           # ID único do arquivo
        total = pacote["total_packets"]       # Total de fragmentos esperados
        username = pacote["username"]         # Nome do usuário que enviou
        conteudo = pacote["data"]            # Conteúdo deste fragmento

        # Inicializa estrutura para o arquivo se for o primeiro fragmento
        if file_id not in arquivos:
            arquivos[file_id] = {
                "packets": {},              # Dicionário dos fragmentos recebidos
                "total": total,            # Total de fragmentos esperados
                "username": username       # Nome do usuário
            }

        # Armazena o fragmento recebido
        arquivos[file_id]["packets"][pacote["packet_num"]] = conteudo
        print(f"[PACOTE] Recebido {pacote['packet_num']}/{total} de {username}")

        # ===== ETAPA 6: VERIFICAÇÃO SE ARQUIVO ESTÁ COMPLETO =====
        if len(arquivos[file_id]["packets"]) == total:
            # Reconstrói a mensagem completa na ordem correta
            mensagem_completa = "".join(
                arquivos[file_id]["packets"][i] for i in range(1, total + 1)
            )
            
            # Formata mensagem com informações do remetente e timestamp
            ip, porta = addr
            timestamp = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            mensagem_formatada = f"{ip}:{porta}/~{username}: {mensagem_completa} {timestamp}"
            print(f"[MSG] {mensagem_formatada}")

            # ===== ETAPA 7: BROADCAST PARA TODOS OS CLIENTES =====
            for cliente_addr, cliente_info in clientes.items():
                if cliente_addr != addr:  # Não reenvia para o remetente
                    server_socket.sendto(mensagem_formatada.encode(), cliente_info['receive_addr'])

            # Remove arquivo processado da memória
            del arquivos[file_id]

    except Exception as e:
        print(f"[ERRO] {e}")
