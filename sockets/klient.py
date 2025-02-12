from socket import *
from threading import Thread
import tkinter as tk

def start_client():
    s = socket()
    host = "10.32.40.224"
    port = 12345
    s.connect((host, port))

    def receive():
        while True:
            try:
                b = s.recv(1024)
                if not b:
                    break
                msg = b.decode("utf-16")
                x1, y1, x2, y2 = map(int, msg.split(","))
                canvas.create_line(x1, y1, x2, y2, fill="black")
            except:
                break

    def send_line(event):
        x1, y1 = event.x, event.y
        x2, y2 = event.x + 1, event.y + 1
        msg = f"{x1},{y1},{x2},{y2}"
        s.send(msg.encode("utf-16"))
        canvas.create_line(x1, y1, x2, y2, fill="black")

    root = tk.Tk()
    root.title("Ritprogram")
    canvas = tk.Canvas(root, width=800, height=600, bg="white")
    canvas.pack()
    canvas.bind("<B1-Motion>", send_line)

    thread = Thread(target=receive)
    thread.start()

    root.mainloop()
    s.close()

if __name__ == "__main__":
    start_client()