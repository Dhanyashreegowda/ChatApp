import socket
import threading
import os

clients = {}  # Dictionary to store client sockets and usernames
active_users = set()  # Set to store active usernames

def handle_client(client_socket):
    try:
        username = client_socket.recv(1024).decode('utf-8')  # Receive username

        # Check if the username is already in use
        if username in active_users:
            client_socket.send("USERNAME_TAKEN".encode('utf-8'))
            client_socket.close()
            return
        else:
            active_users.add(username)  # Add username to active users
            clients[client_socket] = username
            client_socket.send("LOGIN_SUCCESS".encode('utf-8'))
            broadcast(f"{username} has joined the chat.", client_socket)

        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                if message.startswith('FILE:'):
                    filename = message[5:]  # Extract the filename
                    broadcast(f"{username} is sending a file: {filename}", client_socket)

                    # Receive file size
                    file_size = int(client_socket.recv(1024).decode('utf-8'))
                    broadcast(f"{username} is sending a file of size: {file_size} bytes", client_socket)

                    # Receive and save the file
                    with open(filename, 'wb') as f:
                        total_received = 0
                        while total_received < file_size:
                            chunk = client_socket.recv(4096)
                            if not chunk:
                                break
                            f.write(chunk)
                            total_received += len(chunk)

                    # Inform clients that the file has been sent
                    broadcast(f"{username} has sent the file: {filename}. You can download it.", client_socket)

                elif message.startswith('/pm'):
                    # Handle private messages
                    _, recipient_username, private_msg = message.split(' ', 2)
                    send_private_message(username, recipient_username, private_msg)

                else:
                    broadcast(f"{username}: {message}", client_socket)
            else:
                break
    except Exception as e:
        print(f"Error: {e}")

    # Close connection and remove client on disconnect
    client_socket.close()
    if client_socket in clients:
        del clients[client_socket]

    if username in active_users:
        active_users.remove(username)  # Remove the username from active users

    broadcast(f"{username} has left the chat.", client_socket)

def send_private_message(sender_username, recipient_username, message):
    recipient_socket = None
    for client_socket, username in clients.items():
        if username == recipient_username:
            recipient_socket = client_socket
            break

    if recipient_socket:
        try:
            recipient_socket.send(f"Private message from {sender_username}: {message}".encode('utf-8'))
        except Exception as e:
            print(f"Error sending private message: {e}")
    else:
        print(f"User {recipient_username} not found.")

def broadcast(message, client_socket):
    for client in clients:
        if client != client_socket:
            try:
                client.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error sending message: {e}")

def accept_connections(server_socket):
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr} has been established.")
        threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()

# Server setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 12345))
server.listen(5)

print("Server is running...")
accept_connections(server)
