import socket
import re
import json

def send_request(path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('127.0.0.1', 8081))
        request = f'GET {path} HTTP/1.1\r\nHost: 127.0.0.1:8081\r\n\r\n'
        client_socket.send(request.encode())
        response = client_socket.recv(1024).decode('utf-8')
    return response

def parse_product_details(productPageContent):
    productDetails = {}
    for match in re.finditer(r'<b>\s*(.*?)\s*</b>\s*:\s*(.*?)\s*<br>', productPageContent):
        key, value = match.groups()
        productDetails[key] = value
    return productDetails

productContent = send_request('/products')
pages = ['/', '/about', '/contacts']
pageContent = [re.search(r'\n\n(.*)$', send_request(page)).group(1) for page in pages]
productsLinks = re.findall(r'href="product/(\d+)"', productContent)
productInfo = []

for link in productsLinks:
    productPath = f'/product/{link}'
    productPageContent = send_request(productPath)
    productDictionary = parse_product_details(productPageContent)
    productInfo.append(productDictionary)

all_info = {
    'simple_pages': pageContent,
    'product_details': productInfo
}

with open('retrieved_info.json', 'w') as json_file:
    json.dump(all_info, json_file, indent=4)

print(f'Simple page contents:\n{pageContent}')
print('\nProduct details dictionaries:')

for dictionary in productInfo:
    print(dictionary)

print("All information has been saved to 'retrieved_info.json'.")
