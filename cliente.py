import socket
import json
from datetime import datetime
import threading

IP_SERVIDOR = '0.0.0.0'  # IP do servidor (todas interfaces)
PORTA_SERVIDOR = 3000    # Porta do servidor
TAMANHO_FRAGMENTO = 900  # Tamanho máximo de cada pedaço da mensagem

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cria socket UDP
DESTINO = (IP_SERVIDOR, PORTA_SERVIDOR)  # Destino para enviar mensagens

def escutar_servidor(udp):
    while True:
        try:
            dados, _ = udp.recvfrom(1024)
            print("\n" + dados.decode())
        except:
            break  # opcional: tratar desconexão


while True:
    comando = input()

    if comando.lower().startswith("hi, meu nome eh"):
        nome = comando[16:].strip()
        thread_recebimento = threading.Thread(target=escutar_servidor, args=(udp,), daemon=True)
        thread_recebimento.start()
        try:
            udp.sendto(comando.encode(), DESTINO)  # Envia comando de entrada
        except Exception as e:
            print(f"Erro ao enviar nome para o servidor: {e}")
            continue

        print(f"Você entrou na sala como {nome}.")

        while True:
            comando = input()

            if comando == "bye":
                try:
                    udp.sendto(comando.encode(), DESTINO)  # Envia comando de saída
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
                        udp.sendto(mensagem_json.encode(), DESTINO)  # Envia cada pacote

                except FileNotFoundError:
                    print("Erro: a pasta 'arquivos/' não existe. Crie a pasta e tente novamente.")
                    continue
                except Exception as e:
                    print(f"Erro ao salvar a mensagem em arquivo: {e}")
                    continue

        break  # Sai do loop principal após sair da sala

    else:
        print("Comando inválido. Use: hi, meu nome eh <seu_nome>")
