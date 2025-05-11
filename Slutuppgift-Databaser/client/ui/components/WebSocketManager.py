import socketio
import threading

class WebSocketManager:
    def __init__(self, on_new_thread=None, on_thread_deleted=None, on_online_users=None, on_new_post=None):
        self.sio = socketio.Client()
        self.on_new_thread = on_new_thread
        self.on_thread_deleted = on_thread_deleted
        self.on_online_users = on_online_users
        self.on_new_post = on_new_post
        self.current_user = None
        
        # Event hanterare - först kollar vi om det finns en sådan callback, om det finns så anropas den med data från servern
        @self.sio.on('new_thread')
        def handle_new_thread(data):
            if self.on_new_thread:
                self.on_new_thread(data['thread'])
                
        @self.sio.on('thread_deleted')
        def handle_thread_deleted(data):
            if self.on_thread_deleted:
                self.on_thread_deleted(data['thread_id'])
                
        @self.sio.on('online_users')
        def handle_online_users(data):
            if self.on_online_users:
                self.on_online_users(data['users'])

        @self.sio.on('new_post')
        def handle_new_post_event(data):
            if self.on_new_post:
                self.on_new_post(data)
    
    # Ansluter till WebSocket
    def connect(self, current_user=None):
        self.current_user = current_user
        try:
            self.sio.connect('http://localhost:5000')
            # Skicka att användaren är online
            if self.current_user:
                self.sio.emit('user_connected', {'user': self.current_user})
            # Starta WebSocket client i en separat tråd för att undvika blockering av huvudtråden
            threading.Thread(target=self.sio.wait, daemon=True).start()
        except Exception as e:
            print(f"Misslyckades att ansluta till WebSocket server: {str(e)}")
    
    # Kopplar från WebSocket
    def disconnect(self):
        if self.sio.connected:
            self.sio.disconnect() 