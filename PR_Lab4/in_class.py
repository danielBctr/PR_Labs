import socket
import signal
import sys
import threading
import json

HOST = '127.0.0.1'
PORT = 8081
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))

server_socket.listen(5)
print(f"Server is listening on {HOST}:{PORT}")
def load_products_from_json(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

products = load_products_from_json('products.json')

def generate_product_listing():
    product_listing = '<h1>Programming Books Lists</h1><ul>'
    for idx, product in enumerate(products):
        product_listing += f'<li><a href="/product/{idx}">{product["name"]}</a></li>'
    product_listing += '</ul>'
    return product_listing

def handle_product_request(client_socket, product_id):
    if product_id < len(products):
        product = products[product_id]
        response_content = f'<h1>{product["name"]}</h1><p>Author: {product["author"]}</p><p>Price: ${product["price"]}</p><p>Description: {product["description"]}</p>'
        status_code = 200
    else:
        response_content = '404 Not Found'
        status_code = 404

    response = f'HTTP/1.1 {status_code} OK\nContent-Type: text/html\n\n{response_content}'
    client_socket.send(response.encode('utf-8'))
    client_socket.close()

def handle_request(client_socket):
    request_data = client_socket.recv(1024).decode('utf-8')
    print(f"Received Request:\n{request_data}")

    request_lines = request_data.split('\n')

    if not request_lines:
        print("Invalid request: Empty request lines")
        response_content = '400 Bad Request'
        status_code = 400
    else:
        request_line = request_lines[0].strip().split()

        if len(request_line) < 3:
            print("Invalid request: Malformed request line")
            response_content = '400 Bad Request'
            status_code = 400
        else:
            method = request_line[0]
            path = request_line[1]

            response_content = ''
            status_code = 200

            if path == '/':
                response_content = 'This is the Home page.'
            elif path == '/products':
                response_content = generate_product_listing()
            elif path.startswith('/product/'):
                try:
                    product_id = int(path.split('/')[-1])
                    handle_product_request(client_socket, product_id)
                    return
                except ValueError:
                    response_content = 'Invalid product ID'
                    status_code = 400
            elif path == '/about':
                response_content = 'About us:...'
            elif path == '/contacts':
                response_content = 'Contact Us: 444-555-6969'
            else:
                response_content = '404 Not Found'
                status_code = 404

    response = f'HTTP/1.1 {status_code} OK\nContent-Type: text/html\n\n{response_content}'
    client_socket.send(response.encode('utf-8'))
    client_socket.close()

def signal_handler(sig, frame):
    print("\nShutting down the server...")
    server_socket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")

    client_handler = threading.Thread(target=handle_request, args=(client_socket,))
    client_handler.start()

