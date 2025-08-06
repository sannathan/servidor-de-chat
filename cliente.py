import socket
import json
from datetime import datetime
import threading
from protocolrdt3 import make_packet, is_corrupted, extract_data, simulate_corruption

IP_SERVIDOR = '127.0.0.1'  # Ajuste para o IP do servidor real
PORTA_SERVIDOR = 2000
TAMANHO_FRAGMENTO = 800
TIMEOUT = 2
DESTINO = (IP_SERVIDOR, PORTA_SERVIDOR)

# Socket para enviar dados e receber ACKs
send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
send_socket.settimeout(TIMEOUT)

# Socket para receber mensagens do chat
receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receive_socket.bind(('', 0))  # Porta automática para receber mensagens

seq_num = 0

def escutar_servidor(sock):
    while True:
        try:
            dados, _ = sock.recvfrom(1024)
            print("\n" + dados.decode())
        except:
            break

def send_message_rdt3(message_bytes: bytes):
    """Envia mensagem usando RDT 3.0 garantindo ACK."""
    global seq_num
    while True:
        packet = make_packet(message_bytes, seq_num)

        print(f"[CLIENT] Enviando pacote seq_num={seq_num}")
        send_socket.sendto(packet, DESTINO)

        try:
            ack_data, _ = send_socket.recvfrom(1024)
            ack_seq, _ = extract_data(ack_data)

            if ack_seq == seq_num:
                print(f"[CLIENT] ACK válido para seq_num={seq_num}")
                seq_num = 1 - seq_num
                break
            else:
                print("[CLIENT] ACK duplicado, reenviando...")
        except socket.timeout:
            print("[CLIENT] Timeout! Reenviando...")

# Inicia thread para escutar servidor usando socket de recebimento
threading.Thread(target=escutar_servidor, args=(receive_socket,), daemon=True).start()

while True:
    comando = input()

    if comando.lower().startswith("hi, meu nome eh"):
        nome = comando[16:].strip()

        try:
            # Obter porta do socket de recebimento
            receive_port = receive_socket.getsockname()[1]
            
            # Modificar comando para incluir porta de recebimento
            comando_com_porta = f"{comando}:{receive_port}"
            
            send_message_rdt3(comando_com_porta.encode('utf-8'))
        except Exception as e:
            print(f"Erro ao enviar nome: {e}")
            continue

        print(f"Você entrou na sala como {nome}.")

        while True:
            comando = input()

            if comando.lower() == "bye":
                try:
                    send_message_rdt3(comando.encode('utf-8'))
                except Exception as e:
                    print(f"Erro ao enviar bye: {e}")
                break

            else:
                agora = datetime.now().strftime("%H%M%S")
                nome_arquivo = f"arquivos/msg_{agora}.txt"

                try:
                    # Salva mensagem em arquivo
                    with open(nome_arquivo, "w") as f:
                        f.write(comando)

                    # Lê conteúdo
                    with open(nome_arquivo, "r") as f:
                        conteudo = f.read()

                    # Fragmenta
                    blocos = [conteudo[i:i+TAMANHO_FRAGMENTO] for i in range(0, len(conteudo), TAMANHO_FRAGMENTO)]
                    total = len(blocos)
                    file_id = datetime.now().strftime("%H%M%S")

                    for i, bloco in enumerate(blocos):
                        pacote_dict = {
                            "file_id": file_id,
                            "packet_num": i + 1,
                            "total_packets": total,
                            "username": nome,
                            "data": bloco
                        }
                        mensagem_json = json.dumps(pacote_dict).encode('utf-8')
                        send_message_rdt3(mensagem_json)

                except FileNotFoundError:
                    print("Erro: a pasta 'arquivos/' não existe.")
                    continue
                except Exception as e:
                    print(f"Erro ao processar mensagem: {e}")
                    continue

        break

    else:
        print("Comando inválido. Use: hi, meu nome eh <seu_nome>")
