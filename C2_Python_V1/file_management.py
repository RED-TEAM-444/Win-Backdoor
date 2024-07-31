def upload_file(s, file_path):
    with open(file_path, 'rb') as f:
        s.send(f.read())

def download_file(s, file_path):
    with open(file_path, 'wb') as f:
        while True:
            data = s.recv(1024)
            if not data:
                break
            f.write(data)
