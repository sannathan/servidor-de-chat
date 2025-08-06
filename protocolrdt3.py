import hashlib
import json
import random

# --- Configurações ---
TIMEOUT = 2
MAX_RETRIES = 5

# --- Funções base de Checksum ---
def get_checksum(data: bytes) -> str:
    """Gera checksum MD5 a partir de bytes."""
    return hashlib.md5(data).hexdigest()

# --- Funções de Pacote ---
def make_packet(data: bytes, seq_num: int) -> bytes:
    """Cria pacote com número de sequência e checksum."""
    packet_dict = {
        "seq_num": seq_num,
        "data": data.decode("utf-8", errors="ignore")
    }
    checksum = get_checksum(json.dumps(packet_dict).encode("utf-8"))
    packet_dict["checksum"] = checksum
    return json.dumps(packet_dict).encode("utf-8")

def is_corrupted(packet: bytes) -> bool:
    """Verifica se o pacote está corrompido."""
    try:
        pkt = json.loads(packet.decode("utf-8"))
        received_checksum = pkt["checksum"]
        pkt_copy = pkt.copy()
        del pkt_copy["checksum"]
        calc_checksum = get_checksum(json.dumps(pkt_copy).encode("utf-8"))
        return received_checksum != calc_checksum
    except:
        return True

def extract_data(packet: bytes) -> tuple[int, bytes]:
    """
    Retorna (seq_num, data) de um pacote ou ACK.
    Data é retornada em bytes.
    """
    pkt = json.loads(packet.decode("utf-8"))
    seq_num = pkt.get("seq_num", -1)
    data = pkt.get("data", "")
    return seq_num, data.encode("utf-8")

# --- Funções de ACK ---
def make_ack(seq_num: int) -> bytes:
    """Cria pacote de ACK com checksum."""
    ack_dict = {
        "ack": True,
        "seq_num": seq_num
    }
    checksum = get_checksum(json.dumps(ack_dict).encode("utf-8"))
    ack_dict["checksum"] = checksum
    return json.dumps(ack_dict).encode("utf-8")

def is_ack(packet: bytes) -> bool:
    """Verifica se é um ACK."""
    try:
        pkt = json.loads(packet.decode("utf-8"))
        return pkt.get("ack", False) is True
    except:
        return False

# --- Simulação de erro ---
def simulate_corruption(packet: bytes, probability: float = 0.1) -> bytes:
    """Simula corrupção aleatória em um pacote com probabilidade dada."""
    if random.random() < probability:
        corrupted_packet = bytearray(packet)
        idx = random.randint(0, len(corrupted_packet) - 1)
        corrupted_packet[idx] ^= 0xFF
        return bytes(corrupted_packet)
    return packet
