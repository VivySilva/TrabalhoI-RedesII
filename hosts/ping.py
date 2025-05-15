import socket
import sys


def ping(dest_ip, dest_port=5001, mensagem="ping"):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(5)
        s.sendto(mensagem.encode(), (dest_ip, dest_port))
        resposta, _ = s.recvfrom(1024)
        print(
            f"[PING] Resposta de {dest_ip}:{dest_port} → {resposta.decode()}")
        s.close()
    except Exception as e:
        print(f"[PING] Falha ao conectar com {dest_ip}:{dest_port} → {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python ping.py <IP_DESTINO> [PORTA]")
        sys.exit(1)

    ip_destino = sys.argv[1]
    porta_destino = int(sys.argv[2]) if len(sys.argv) > 2 else 5001

    ping(ip_destino, porta_destino)
