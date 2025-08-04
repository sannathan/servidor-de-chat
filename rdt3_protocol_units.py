import hashlib
import json
import random
import socket
import time

TIMEOUT = 2
MAX_RETRIES = 5


def get_checksum(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()

def make_packet(data: bytes, seq_num: int) -> bytes:
    packet_dict = {
        'seq_num': seq_num,
        'data': data.decode('utf-8'),
    }
    checksum = get_checksum(json.dumps(packet_dict).encode('utf-8'))
    packet_dict['checksum'] = checksum
    return json.dumps(packet_dict).encode('utf-8')

def is_corrupted(packet: bytes) -> bool:
    try:
        pkt = json.loads(packet.decode('utf-8'))
        received_checksum = pkt['checksum']
        pkt_copy = pkt.copy()
        del pkt_copy['checksum']
        calc_checksum = get_checksum(json.dumps(pkt_copy).encode('utf-8'))
        return received_checksum != calc_checksum
    except:
        return True

def extract_data(packet: bytes) -> tuple[int, bytes]:
    pkt = json.loads(packet.decode('utf-8'))
    return pkt['seq_num'], pkt['data'].encode('utf-8')

def make_ack(seq_num: int) -> bytes:
    ack = {
        'ack': True,
        'seq_num': seq_num
    }
    ack['checksum'] = get_checksum(json.dumps({'ack': True, 'seq_num': seq_num}).encode('utf-8'))
    return json.dumps(ack).encode('utf-8')

def is_ack(packet: bytes) -> bool:
    try:
        pkt = json.loads(packet.decode('utf-8'))
        return pkt.get('ack', False)
    except:
        return False

def simulate_corruption(packet: bytes, probability: float = 0.1) -> bytes:
    if random.random() < probability:
        corrupted_packet = bytearray(packet)
        idx = random.randint(0, len(corrupted_packet) - 1)
        corrupted_packet[idx] ^= 0xFF
        return bytes(corrupted_packet)
    return packet

def rdt_send(sock: socket.socket, address, data: bytes):
    seq_num = 0
    retries = 0

    while retries < MAX_RETRIES:
        packet = make_packet(data, seq_num)
        sock.sendto(packet, address)
        print(f"[CLIENT] Enviado pacote com seq_num={seq_num}")

        sock.settimeout(TIMEOUT)
        try:
            ack_packet, _ = sock.recvfrom(2048)
            if is_corrupted(ack_packet):
                print("[CLIENT] ACK corrompido, reenviando...")
            elif is_ack(ack_packet):
                ack = json.loads(ack_packet.decode('utf-8'))
                if ack['seq_num'] == seq_num:
                    print(f"[CLIENT] ACK válido recebido para seq_num={seq_num}")
                    break
                else:
                    print("[CLIENT] ACK com número de sequência incorreto")
        except socket.timeout:
            print("[CLIENT] Timeout! Reenviando pacote...")
        retries += 1

    if retries == MAX_RETRIES:
        print("[CLIENT] Número máximo de tentativas alcançado. Abortando envio.")
