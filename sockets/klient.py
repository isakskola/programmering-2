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
                color, coords = msg.split(",", 1)
                coords = list(map(int, coords.split(",")))
                canvas.create_line(*coords, fill=color, width=3)
            except:
                break

    def send_line(event):
        x1, y1 = event.x, event.y
        if hasattr(send_line, 'last_x') and hasattr(send_line, 'last_y'):
            x2, y2 = send_line.last_x, send_line.last_y
        else:
            x2, y2 = x1, y1
        msg = f"{x1},{y1},{x2},{y2}"
        s.send(msg.encode("utf-16"))
        canvas.create_line(x1, y1, x2, y2, fill="black", width=3)
        send_line.last_x, send_line.last_y = x1, y1

    def reset_line(event):
        if hasattr(send_line, 'last_x'):
            del send_line.last_x
        if hasattr(send_line, 'last_y'):
            del send_line.last_y

    root = tk.Tk()
    root.title("Ritprogram")
    canvas = tk.Canvas(root, width=800, height=600, bg="white")
    canvas.pack()
    canvas.bind("<B1-Motion>", send_line)
    canvas.bind("<ButtonRelease-1>", reset_line)

    thread = Thread(target=receive)
    thread.start()

    root.mainloop()
    s.close()

if __name__ == "__main__":
    start_client()