import socket
import json
from datetime import datetime
import threading
from protocolrdt3 import make_packet, is_corrupted, extract_data, simulate_corruption

# ===== CONFIGURAÇÕES DO CLIENTE =====
IP_SERVIDOR = '127.0.0.1'  # Endereço IP do servidor
PORTA_SERVIDOR = 2000       # Porta onde o servidor está rodando
TAMANHO_FRAGMENTO = 800     # Tamanho máximo de cada fragmento de mensagem
TIMEOUT = 2                 # Timeout em segundos para recebimento de ACK
DESTINO = (IP_SERVIDOR, PORTA_SERVIDOR)  # Tupla com destino do servidor

# ===== CONFIGURAÇÃO DOS SOCKETS =====
# Socket dedicado para enviar dados e receber ACKs do protocolo RDT3
send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
send_socket.settimeout(TIMEOUT)

# Socket dedicado para receber mensagens do chat (evita conflito com ACKs)
receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receive_socket.bind(('', 0))  # Porta automática para receber mensagens

# ===== VARIÁVEIS GLOBAIS =====
seq_num = 0  # Número de sequência para protocolo RDT3 (alterna entre 0 e 1)

# ===== FUNÇÕES AUXILIARES =====

def escutar_servidor(sock):
    """
    Thread dedicada para escutar mensagens do servidor.
    Executa em paralelo para não bloquear a entrada do usuário.
    
    Args:
        sock: Socket UDP para receber mensagens
    """
    while True:
        try:
            dados, _ = sock.recvfrom(1024)
            print("\n" + dados.decode())  # Mostra mensagem recebida
        except:
            break  # Sai do loop se houver erro (ex: socket fechado)

def send_message_rdt3(message_bytes: bytes):
    """
    Envia mensagem usando protocolo RDT 3.0 com garantia de entrega.
    Implementa stop-and-wait com retransmissão em caso de timeout ou ACK duplicado.
    
    Args:
        message_bytes: Mensagem em bytes para enviar
    """
    global seq_num
    
    while True:  # Loop até receber ACK correto
        # Cria pacote com número de sequência e checksum
        packet = make_packet(message_bytes, seq_num)
        
        # Envia pacote para o servidor
        send_socket.sendto(packet, DESTINO)

        try:
            # Aguarda ACK do servidor
            ack_data, _ = send_socket.recvfrom(1024)
            ack_seq, _ = extract_data(ack_data)

            # Verifica se o ACK corresponde ao pacote enviado
            if ack_seq == seq_num:
                # ACK correto recebido - alterna número de sequência
                seq_num = 1 - seq_num  # Alterna entre 0 e 1
                break  # Sai do loop, envio concluído
            else:
                print("[CLIENT] ACK duplicado, reenviando...")
                
        except socket.timeout:
            # Timeout - servidor não respondeu, reenvia pacote
            print("[CLIENT] Timeout! Reenviando...")

# ===== PROGRAMA PRINCIPAL =====

# Inicia thread para escutar mensagens do servidor em paralelo
threading.Thread(target=escutar_servidor, args=(receive_socket,), daemon=True).start()

# Loop principal - aguarda comandos do usuário
while True:
    comando = input()

    # ===== COMANDO DE ENTRADA NA SALA =====
    if comando.lower().startswith("hi, meu nome eh"):
        nome = comando[16:].strip()  # Extrai o nome do comando

        try:
            # Obtém a porta do socket de recebimento para informar ao servidor
            receive_port = receive_socket.getsockname()[1]
            
            # Cria comando modificado incluindo a porta de recebimento
            # Formato: "hi, meu nome eh João:12345" onde 12345 é a porta
            comando_com_porta = f"{comando}:{receive_port}"
            
            # Envia comando de entrada usando protocolo RDT3
            send_message_rdt3(comando_com_porta.encode('utf-8'))
            
        except Exception as e:
            print(f"Erro ao enviar nome: {e}")
            continue

        print(f"Você entrou na sala como {nome}.")

        # ===== LOOP INTERNO - USUÁRIO CONECTADO =====
        while True:
            comando = input()

            # === COMANDO DE SAÍDA ===
            if comando.lower() == "bye":
                try:
                    # Envia comando de saída para o servidor
                    send_message_rdt3(comando.encode('utf-8'))
                except Exception as e:
                    print(f"Erro ao enviar bye: {e}")
                break  # Sai do loop interno, volta ao loop principal

            # === ENVIO DE MENSAGEM ===
            else:
                # Gera timestamp único para identificar o arquivo
                agora = datetime.now().strftime("%H%M%S")
                nome_arquivo = f"arquivos/msg_{agora}.txt"

                try:
                    # === ETAPA 1: SALVAR MENSAGEM EM ARQUIVO ===
                    with open(nome_arquivo, "w") as f:
                        f.write(comando)  # Salva mensagem digitada

                    # === ETAPA 2: LER CONTEÚDO DO ARQUIVO ===
                    with open(nome_arquivo, "r") as f:
                        conteudo = f.read()

                    # === ETAPA 3: FRAGMENTAÇÃO ===
                    # Divide o conteúdo em blocos menores para envio
                    blocos = [conteudo[i:i+TAMANHO_FRAGMENTO] 
                             for i in range(0, len(conteudo), TAMANHO_FRAGMENTO)]
                    total = len(blocos)
                    file_id = datetime.now().strftime("%H%M%S")  # ID único do arquivo

                    # === ETAPA 4: ENVIO DOS FRAGMENTOS ===
                    for i, bloco in enumerate(blocos):
                        # Cria pacote JSON com metadados do fragmento
                        pacote_dict = {
                            "file_id": file_id,           # ID único do arquivo
                            "packet_num": i + 1,          # Número do pacote (1, 2, 3...)
                            "total_packets": total,       # Total de pacotes da mensagem
                            "username": nome,             # Nome do usuário
                            "data": bloco                 # Conteúdo do fragmento
                        }
                        
                        # Converte para JSON e envia usando RDT3
                        mensagem_json = json.dumps(pacote_dict).encode('utf-8')
                        send_message_rdt3(mensagem_json)

                except FileNotFoundError:
                    print("Erro: a pasta 'arquivos/' não existe.")
                    continue
                except Exception as e:
                    print(f"Erro ao processar mensagem: {e}")
                    continue

        break  # Sai do loop principal após comando "bye"

    # ===== COMANDO INVÁLIDO =====
    else:
        print("Comando inválido. Use: hi, meu nome eh <seu_nome>")
