'''
Module that contains methods and classes that are used for the audio in our program.
'''
import wave
from threading import Thread
import pyaudio

class AudioManager:
    '''
    Contains the helper function play(String:filepath)
    '''


    def __play(self, filepath):
        chunk = 1024

        audio_file = wave.open(filepath, "rb")

        out_p = pyaudio.PyAudio()
        out_stream = out_p.open(#Creates a stream used to output the audio
            format = out_p.get_format_from_width(audio_file.getsampwidth()),
            channels = audio_file.getnchannels(),
            rate = audio_file.getframerate(),
            output = True
        )

        print("Playing Audio:", filepath)
        data = audio_file.readframes(chunk)
        while data != b"": #Reads through the audio files and plays it to the out_stream
            out_stream.write(data)
            data = audio_file.readframes(chunk)

        out_stream.close()
        print("Audio", filepath, "has ended.")

    def play(self, filepath):
        '''
        Takes a file path to a .wav file and plays the audio file.
        
        Requires filepath to be the fileparth from the audio.py file to the .wav file.
        '''
        Thread(target=AudioManager.__play, args=[filepath], daemon= True).start()
