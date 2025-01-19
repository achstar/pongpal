import socket
HOST = '0.0.0.0'
PORT = 5005
client_sockets = []
print("Initializing connection")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server listening on {HOST}:{PORT}")

    # Accept a single client connection
    while len(client_sockets) < 2:
        client_socket, client_address = server_socket.accept()
        client_sockets.append(client_socket)
        print(f"Connection established with {client_address}")

    print("Both clients connected!")