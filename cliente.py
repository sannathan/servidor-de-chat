import socket
import json
from datetime import datetime
import threading
from protocolrdt3 import make_packet, is_ack, is_corrupted, extract_data, make_ack, simulate_corruption

IP_SERVIDOR = '0.0.0.0'  # IP do servidor (todas interfaces)
PORTA_SERVIDOR = 2000    # Porta do servidor
TAMANHO_FRAGMENTO = 800  # Tamanho máximo de cada pedaço da mensagem menor que 1024 para garantir que somado com cabeçalho não passe
TIMEOUT = 2 #segundos
DESTINO = (IP_SERVIDOR, PORTA_SERVIDOR)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(TIMEOUT)
seq_num = 0

def escutar_servidor(sock):
    while True:
        try:
            dados, _ = sock.recvfrom(1024)
            print("\n" + dados.decode())
        except:
            break


def send_message_rdt3(message):
    global seq_num
    packet = make_packet(message.encode('utf-8'), seq_num)

    while True:
        print(f"[CLIENT] Enviando pacote com seq_num={seq_num}")
        client_socket.sendto(packet, DESTINO)

        try:
            ack_data, _ = client_socket.recvfrom(1024)
            print("[CLIENT] ACK recebido")

            if is_corrupted(ack_data):
                print("[CLIENT] ACK corrompido, reenviando pacote...")
                continue

            ack_pkt = ack_data.decode('utf-8')
            ack_pkt = eval(ack_pkt)
            if ack_pkt['seq_num'] == seq_num:
                print(f"[CLIENT] ACK válido recebido para seq_num={seq_num}")
                seq_num = 1 - seq_num
                break
            else:
                print("[CLIENT] ACK duplicado, reenviando pacote...")

        except socket.timeout:
            print("[CLIENT] Timeout! Reenviando pacote...")

while True:
    comando = input()

    if comando.lower().startswith("hi, meu nome eh"):
        nome = comando[16:].strip()
        thread_recebimento = threading.Thread(target=escutar_servidor, args=(client_socket,), daemon=True)
        thread_recebimento.start()
        try:
            send_message_rdt3(comando)
                    # Envia comando de entrada
        except Exception as e:
            print(f"Erro ao enviar nome para o servidor: {e}")
            continue

        print(f"Você entrou na sala como {nome}.")

        while True:
            comando = input()

            if comando == "bye":
                try:
                    send_message_rdt3(comando) # Envia comando de saída
                except Exception as e:
                    print(f"Erro ao enviar bye: {e}")
                break

            else:
                agora = datetime.now().strftime("%H%M%S")
                nome_arquivo = f"arquivos/msg_{agora}.txt"  # Nome do arquivo temporário

                try:
                    with open(nome_arquivo, "w") as f:
                        f.write(comando)  # Salva mensagem no arquivo
                    with open(nome_arquivo, "rb") as f:
                        conteudo = f.read()  # Lê conteúdo em bytes

                    # Divide o conteúdo em pedaços de até TAMANHO_FRAGMENTO bytes
                    blocos = [conteudo[i:i+TAMANHO_FRAGMENTO] for i in range(0, len(conteudo), TAMANHO_FRAGMENTO)]
                    total = len(blocos)
                    file_id = datetime.now().strftime("%H%M%S")  # ID do arquivo

                    for i, bloco in enumerate(blocos):
                        pacote = {
                            "file_id": file_id,
                            "packet_num": i + 1,
                            "total_packets": total,
                            "username": nome,
                            "data": bloco.decode('utf-8', errors='ignore')  # Decodifica para texto
                        }
                        mensagem_json = json.dumps(pacote)
                        send_message_rdt3(mensagem_json)  # Envia cada pacote

                except FileNotFoundError:
                    print("Erro: a pasta 'arquivos/' não existe. Crie a pasta e tente novamente.")
                    continue
                except Exception as e:
                    print(f"Erro ao salvar a mensagem em arquivo: {e}")
                    continue

        break  # Sai do loop principal após sair da sala

    else:
        print("Comando inválido. Use: hi, meu nome eh <seu_nome>")
