import os
import io
import wave
import tempfile
import traceback
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

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
        # Verify the file exists and is not empty
        if not os.path.exists(audio_file_path):
            print(f"Error: Audio file not found at {audio_file_path}")
            return None
            
        file_size = os.path.getsize(audio_file_path)
        if file_size == 0:
            print("Error: Audio file is empty")
            return None
            
        print(f"Attempting to transcribe file: {audio_file_path} (Size: {file_size} bytes)")
        
        try:
            # Convert audio to WAV format if needed
            audio = AudioSegment.from_file(audio_file_path)
            print(f"Original audio info - Channels: {audio.channels}, Frame rate: {audio.frame_rate}, Duration: {len(audio)/1000}s")
            
            # Convert to mono and set sample rate to 16kHz if needed
            if audio.channels > 1:
                audio = audio.set_channels(1)
                print("Converted to mono")
            if audio.frame_rate != 16000:
                audio = audio.set_frame_rate(16000)
                print(f"Converted to 16kHz (was {audio.frame_rate}Hz)")
            
            # Save as WAV in memory
            wav_io = io.BytesIO()
            audio.export(wav_io, format='wav')
            wav_io.seek(0)
            
            # Use the in-memory WAV file for recognition
            with sr.AudioFile(wav_io) as source:
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Recording audio...")
                audio_data = self.recognizer.record(source)
                print("Sending to Google Speech Recognition...")
                try:
                    text = self.recognizer.recognize_google(audio_data)
                    print(f"Transcription successful: {text}")
                    return text
                except sr.UnknownValueError:
                    print("Error: Google Speech Recognition could not understand the audio")
                    return None
                except sr.RequestError as e:
                    print(f"Error: Could not request results from Google Speech Recognition service; {e}")
                    return None
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in transcription: {str(e)}\n{error_details}")
            
            # Provide more specific error messages
            if "Audio data must be audio data" in str(e):
                print("Error: The audio format might be incompatible. Try converting to WAV format first.")
            elif "Invalid audio data" in str(e):
                print("Error: The audio data is invalid or corrupted.")
            elif "recognition connection failed" in str(e).lower():
                print("Error: Could not connect to Google's servers. Check your internet connection.")
                
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
