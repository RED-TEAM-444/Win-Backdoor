import pyaudio
import wave
import os

def record_audio(output_file, duration):
    chunk = 1024
    format = pyaudio.paInt16
    channels = 2
    rate = 44100

    p = pyaudio.PyAudio()
    stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

    frames = []

    for _ in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    output_path = os.path.join("recordings", output_file)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    wf = wave.open(output_path, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()
