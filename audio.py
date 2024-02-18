import wave
import pyaudio
from threading import Thread


class AudioManager:
    

    def __play(filepath):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        p = pyaudio.PyAudio()

        audio_file = wave.open(filepath, "rb")

        out_p = pyaudio.PyAudio()
        out_stream = out_p.open(#Creates a stream used to output the audio
            format = out_p.get_format_from_width(audio_file.getsampwidth()),
            channels = audio_file.getnchannels(),
            rate = audio_file.getframerate(),
            output = True
        )

        print("Playing Audio")
        data = audio_file.readframes(CHUNK)
        while data != b"": #Reads through the audio files and plays it to the out_stream
            out_stream.write(data)
            data = audio_file.readframes(CHUNK)

        out_stream.close()
        print("Audio has ended")
        return

    #Creates and starts a thread that plays the specificed .wav file. Threading used to keep program from waiting for the audio to finish playing
    #the filepath argument only accepts a relative file path if that is the path from the audio.py file to the sound file for this project the file paths should go sounds/[name of file]
    def play(filepath):
        Thread(target=AudioManager.__play, args=[filepath], daemon= True).start()
