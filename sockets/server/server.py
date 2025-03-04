import socket
import threading
import json

HOST = 'localhost'
PORT = 12345

clients = {}
positions = {}

def handle_client(conn, addr):
    client_id = f"{addr[0]}:{addr[1]}"
    print(f"Ny anslutning: {addr}")
    clients[client_id] = {'conn': conn, 'address': addr, 'color': f'#{hex(hash(addr) % 0xFFFFFF)[2:]:0>6}'}

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            position_data = json.loads(data.decode())
            positions[client_id] = position_data
            
            broadcast_positions()
    except Exception as e:
        print(f"Kunde inte hantera klient {addr}: {e}")
    finally:
        conn.close()
        if client_id in clients:
            del clients[client_id]
        if client_id in positions:
            del positions[client_id]
        print(f"Anslutning stängd: {addr}")

def broadcast_positions():
    if not positions:
        return
        
    serializable_positions = []
    for client_id, position in positions.items():
        serializable_positions.append(position)
        
    try:
        data = json.dumps(serializable_positions).encode()
        for client_id, client_info in clients.items():
            try:
                client_info['conn'].sendall(data)
            except Exception as e:
                print(f"Kunde inte skicka till klient {client_id}: {e}")
    except Exception as e:
        print(f"Kunde inte skicka positioner alls: {e}")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print("Servern lyssnar på", (HOST, PORT))
        
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()