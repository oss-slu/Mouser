'''
Module that contains methods and classes that are used for the audio in our program.
'''
import wave
from threading import Thread, Lock
import sqlite3 as sql
import os
import pyaudio

class AudioManager:
    '''
    Contains the helper function play(String:filepath)
    '''
    _lock = Lock()
    _is_playing = False

    @staticmethod
    def __play(filepath): #pylint: disable= no-self-argument
        chunk = 1024
        try:
            # Ensure the file exists before opening
            if not os.path.exists(filepath):
                print(f"Error: Audio file {filepath} not found.")
                return

            with AudioManager._lock:
                AudioManager._is_playing = True
                audio_file = wave.open(filepath, "rb")
                out_p = pyaudio.PyAudio()

                out_stream = out_p.open(
                    format=out_p.get_format_from_width(audio_file.getsampwidth()),
                    channels=audio_file.getnchannels(),
                    rate=audio_file.getframerate(),
                    output=True
                )

            print(f"Playing Audio: {filepath}")
            data = audio_file.readframes(chunk)

            # Stream audio data in chunks
            while data:
                out_stream.write(data)
                data = audio_file.readframes(chunk)

        except sql.Error as e:
            print(f"Error playing audio: {e}")

        finally:
            # Ensure resources are properly closed
            try:
                out_stream.stop_stream()
                out_stream.close()
                out_p.terminate()
                audio_file.close()
                AudioManager._is_playing = False
                print(f"Audio {filepath} has ended.")
            except sql.Error as cleanup_error:
                print(f"Error during audio cleanup: {cleanup_error}")

    @staticmethod
    def play(filepath):
        """Play audio asynchronously in a separate thread."""
        if os.path.exists(filepath):
            if not AudioManager._is_playing:
                Thread(target=AudioManager.__play, args=(filepath,), daemon=True).start()
            else:
                print("Audio is already playing. Please wait.")
        else:
            print(f"Error: Audio file {filepath} does not exist.")
