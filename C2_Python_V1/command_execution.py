import subprocess

def execute_command(command):
    return subprocess.run(command, shell=True, capture_output=True, text=True)
