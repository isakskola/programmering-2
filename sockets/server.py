from socket import *
from threading import Thread
import random

clients = []
colors = {}

def handle_client(conn, addr):
    print("En klient anslöt från adressen", addr)
    color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    colors[conn] = color
    while True:
        try:
            b = conn.recv(1024)
            if not b:
                break
            msg = b.decode("utf-16")
            print(f"Meddelande från {addr}: {msg}")
            broadcast(f"{color},{msg}", conn)
        except:
            break
    conn.close()
    clients.remove(conn)
    del colors[conn]

def broadcast(msg, sender_conn):
    for client in clients:
        if client != sender_conn:
            client.send(msg.encode("utf-16"))

def start_server():
    s = socket()
    host = "10.32.40.224"
    port = 12345
    s.bind((host, port))
    s.listen()
    print("Servern är igång på port 12345! Väntar på att en klient ska ansluta...")
    while True:
        conn, addr = s.accept()
        clients.append(conn)
        thread = Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()