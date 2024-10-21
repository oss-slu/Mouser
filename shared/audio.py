'''
Module that contains methods and classes that are used for the audio in our program.
'''
import wave
from threading import Thread
import pyaudio
import os

class AudioManager:
    @staticmethod
    def __play(filepath):
        chunk = 1024
        try:
            # Ensure the file exists before opening
            if not os.path.exists(filepath):
                print(f"Error: Audio file {filepath} not found.")
                return

            audio_file = wave.open(filepath, "rb")
            out_p = pyaudio.PyAudio()

            # Create an output stream
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

        except Exception as e:
            print(f"Error playing audio: {e}")

        finally:
            # Ensure resources are properly closed
            try:
                out_stream.stop_stream()
                out_stream.close()
                out_p.terminate()
                audio_file.close()
                print(f"Audio {filepath} has ended.")
            except Exception as cleanup_error:
                print(f"Error during audio cleanup: {cleanup_error}")

    @staticmethod
    def play(filepath):
        """Play audio asynchronously in a separate thread."""
        if os.path.exists(filepath):
            Thread(target=AudioManager.__play, args=(filepath,), daemon=True).start()
        else:
            print(f"Error: Audio file {filepath} does not exist.")
