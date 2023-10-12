import socket
import threading
import json
import os
import uuid

HOST = '127.0.0.1'
PORT = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Server is listening on {HOST}:{PORT}")

clients = {}
media_dir = "SERVER_MEDIA"

def create_client_media_folder(client_socket):
    unique_id = str(uuid.uuid4())
    client_dir = os.path.join(media_dir, unique_id)
    os.makedirs(client_dir, exist_ok=True)
    return client_dir

def create_room_media_folder(room):
    room_dir = os.path.join(media_dir, room)
    os.makedirs(room_dir, exist_ok=True)
    return room_dir

def get_room_of_client(client_socket):
    for room, client_list in clients.items():
        if client_socket in client_list:
            return room
    return None

def get_client_name(client_socket):
    for room, client_list in clients.items():
        if client_socket in client_list:
            for client in client_list:
                return client.getpeername()[0]

def broadcast_message(sender, room, text):
    message = {
        "type": "message",
        "payload": {
            "sender": sender,
            "room": room,
            "text": text
        }
    }
    message_json = json.dumps(message)
    for client in clients[room]:
        client.send(message_json.encode('utf-8'))

def handle_client(client_socket, client_address):
    print(f"Accepted connection from {client_address}")
    try:
        while True:
            message_json = client_socket.recv(1024).decode('utf-8')
            if not message_json:
                break

            message = json.loads(message_json)

            if message["type"] == "connect":
                name = message["payload"]["name"]
                room = message["payload"]["room"]
                clients.setdefault(room, []).append(client_socket)

                ack_message = {
                    "type": "connect_ack",
                    "payload": {
                        "message": "Connected to the room."
                    }
                }
                client_socket.send(json.dumps(ack_message).encode('utf-8'))

                broadcast_message("Server", room, f"{name} joined the room.")

            elif message["type"] == "message":
                sender = message["payload"]["sender"]
                room = message["payload"]["room"]
                text = message["payload"]["text"]

                broadcast_message(sender, room, text)

            elif message["type"] == "upload":
                file_path = message["payload"]["path"]
                room = get_room_of_client(client_socket)
                filename = os.path.basename(file_path)
                server_media_dir = os.path.join(create_room_media_folder(room), filename)

                if os.path.exists(server_media_dir):
                    client_socket.send(f"File {filename} already exists on the server.".encode('utf-8'))
                elif os.path.exists(file_path):
                    with open(file_path, "rb") as file:
                        file_data = file.read()

                    with open(server_media_dir, "wb") as server_file:
                        server_file.write(file_data)

                    broadcast_message("Server", room, f"User {get_client_name(client_socket)} uploaded {filename}")
                else:
                    client_socket.send(f"File {filename} doesn't exist.".encode('utf-8'))

            elif message["type"] == "download":
                filename = message["payload"]["filename"]
                room = get_room_of_client(client_socket)
                server_media_dir = os.path.join(create_room_media_folder(room), filename)

                if os.path.exists(server_media_dir):
                    with open(server_media_dir, "rb") as file:
                        file_data = file.read()

                    download_message = {
                        "type": "download",
                        "payload": {
                            "filename": filename,
                            "data": file_data
                        }
                    }
                    client_socket.send(json.dumps(download_message).encode('utf-8'))
                else:
                    client_socket.send(f"The {filename} doesn't exist.".encode('utf-8'))

    except Exception as e:
        print(f"Error: {e}")

    finally:
        room = get_room_of_client(client_socket)
        if room:
            clients[room].remove(client_socket)
            broadcast_message("Server", room, f"A user left the room.")

        client_socket.close()
        print(f"Connection closed with {client_address}")

while True:
    client_socket, client_address = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()

