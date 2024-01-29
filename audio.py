import wave
import pyaudio


class AudioManager:
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    p = pyaudio.PyAudio()

    def play(self, filepath):

        audio_file = wave.open(filepath, "rb")

        out_p = pyaudio.PyAudio()
        out_stream = out_p.open(#Creates a stream used to output the audio
            format = out_p.get_format_from_width(audio_file.getsampwidth()),
            channels = audio_file.getnchannels(),
            rate = audio_file.getframerate(),
            output = True
        )

        print("Playing Audio")
        data = audio_file.readframes(self.CHUNK)
        while data != b"": #Reads through the audio files and plays it to the out_stream
            out_stream.write(data)
            data = audio_file.readframes(self.CHUNK)

        out_stream.close()
        print("Audio has ended")
