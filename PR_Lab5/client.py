import socket
import threading
import json
import os
import base64

HOST = '127.0.0.1'
PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print(f"Connected to {HOST}:{PORT}")

def receive_messages():
    while True:
        try:
            message_json = client_socket.recv(1024).decode('utf-8')
            if not message_json:
                break

            message = json.loads(message_json)

            if message["type"] == "connect_ack":
                print(message["payload"]["message"])
            elif message["type"] == "message":
                sender = message["payload"]["sender"]
                room = message["payload"]["room"]
                text = message["payload"]["text"]
                print(f"{sender} ({room}): {text}")

            elif message["type"] == "download":
                filename = message["payload"]["filename"]
                file_data = message["payload"]["data"]

                # Save the file in the client's media folder (CLIENT_MEDIA)
                with open(os.path.join(client_media_folder, filename), "wb") as file:
                    if os.path.splitext(filename)[1].lower() in [".jpg", ".jpeg", ".png"]:
                        file.write(base64.b64decode(file_data))
                    else:
                        # Otherwise, save it as text data
                        file.write(file_data.encode('utf-8'))

                print(f"File {filename} downloaded and saved in {client_media_folder}.")

        except Exception as e:
            print(f"Error: {e}")
            break

receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

name = input("Enter your name: ")
room = input("Enter the room name you want to join: ")

connect_message = {
    "type": "connect",
    "payload": {
        "name": name,
        "room": room
    }
}
client_socket.send(json.dumps(connect_message).encode('utf-8'))

# Create a separate media folder for the client
client_media_folder = f"CLIENT_MEDIA/{name}"
os.makedirs(client_media_folder, exist_ok=True)

while True:
    message = input("Enter a message or file command (e.g., 'upload: <file_path>', 'download: <filename>', or 'exit' to quit): ")
    if message.lower() == 'exit':
        break

    # For uploading a file(txt or image)
    if message.lower().startswith("upload: "):
        file_path = message.split(" ")[1]
        if os.path.exists(file_path):
            upload_message = {
                "type": "upload",
                "payload": {
                    "path": file_path
                }
            }
            client_socket.send(json.dumps(upload_message).encode('utf-8'))
        else:
            print(f"File doesn't exist: {file_path}")

    # For downloading a file(txt or image)
    elif message.lower().startswith("download: "):
        filename = message.split(" ")[1]
        download_message = {
            "type": "download",
            "payload": {
                "filename": filename
            }
        }
        client_socket.send(json.dumps(download_message).encode('utf-8'))
    else:
        message_data = {
            "type": "message",
            "payload": {
                "sender": name,
                "room": room,
                "text": message
            }
        }
        client_socket.send(json.dumps(message_data).encode('utf-8'))

client_socket.close()
