import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext

class ChatClient:
    def __init__(self, root, client_socket, username):
        self.client_socket = client_socket
        self.username = username
        
        # Set up the main window
        self.root = root
        self.root.title("Chat Client")
        self.root.geometry("400x400")  # Set fixed dimensions
        self.root.resizable(False, False)  # Make window non-resizable

        # Create a label to display username
        self.username_label = tk.Label(self.root, text=f"Logged in as: {self.username}", anchor=tk.W, padx=10, pady=5)
        self.username_label.pack(fill=tk.X)

        # Create a text area to display chat messages
        self.chat_display = tk.Text(self.root, wrap=tk.WORD, state='disabled', height=15)
        self.chat_display.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Create an entry box for typing messages
        self.message_entry = tk.Entry(self.root)
        self.message_entry.pack(padx=10, pady=5, fill=tk.X)
        self.message_entry.bind("<Return>", self.send_message)

        # Create a send button
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(padx=10, pady=5)

        # Start a thread to receive messages
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.display_message(message)
                else:
                    break
            except:
                self.display_error("Connection Error", "Lost connection to the server.")
                self.client_socket.close()
                break

    def send_message(self, event=None):
        message = self.message_entry.get()
        if message:
            try:
                message_to_send = f"{self.username}: {message}\n"
                self.client_socket.send(message_to_send.encode('utf-8'))
                self.display_message(message_to_send, align='right')  # Display own message on the right
                self.message_entry.delete(0, tk.END)
            except:
                self.display_error("Connection Error", "Lost connection to the server.")
                self.client_socket.close()

    def display_message(self, message, align='left'):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, message, align)
        self.chat_display.yview(tk.END)
        self.chat_display.config(state='disabled')

    def display_error(self, title, message):
        messagebox.showerror(title, message)

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window while we ask for the username

    username = None
    while not username:
        username = simpledialog.askstring("Username", "Enter your username:", parent=root)
        if not username:
            messagebox.showerror("Error", "Username cannot be empty. Please enter a valid username.")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('127.0.0.1', 5555))
    except ConnectionError:
        messagebox.showerror("Connection Error", "Unable to connect to the server.")
        return

    # Initialize the chat client with GUI
    root.deiconify()  # Show the main window after getting the username
    client = ChatClient(root, client_socket, username)

    root.mainloop()

if __name__ == "__main__":
    main()
