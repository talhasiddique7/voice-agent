import os
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import wave

class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000  # Adjust based on your environment

    def save_audio(self, audio_data, file_path):
        """Save audio data to a WAV file"""
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write as WAV file
        with wave.open(file_path, 'wb') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)   # 2 bytes per sample (16-bit)
            wf.setframerate(16000)  # 16kHz sample rate
            wf.writeframes(audio_data)
            
        return file_path

    def transcribe_audio(self, audio_file_path):
        """Transcribe audio file to text"""
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                return text
        except Exception as e:
            print(f"Error in transcription: {str(e)}")
            return None

    def text_to_speech(self, text, lang='en', slow=False):
        """Convert text to speech and return the audio file path"""
        try:
            tts = gTTS(text=text, lang=lang, slow=slow)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file_path = fp.name
                tts.save(temp_file_path)
            return temp_file_path
        except Exception as e:
            print(f"Error in text-to-speech: {str(e)}")
            return None

    def play_audio(self, audio_file_path):
        """Play an audio file"""
        try:
            audio = AudioSegment.from_file(audio_file_path)
            play(audio)
            return True
        except Exception as e:
            print(f"Error playing audio: {str(e)}")
            return False
