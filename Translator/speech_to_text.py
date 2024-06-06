from pydub import AudioSegment
import speech_recognition as sr
import os


def convert_ogg_to_wav(oga_file_path, wav_file_path):
    if not os.path.exists(oga_file_path):
        print(f"Error: The file {oga_file_path} does not exist.")
        return
    audio = AudioSegment.from_file(oga_file_path, format="ogg")
    audio.export(wav_file_path, format="wav")
    print(f"Converted {oga_file_path} to {wav_file_path}")


def convert_mp3_to_wav(mp3_file_path, wav_file_path):
    if not os.path.exists(mp3_file_path):
        print(f"Error: The file {mp3_file_path} does not exist.")
        return
    audio = AudioSegment.from_mp3(mp3_file_path)
    audio.export(wav_file_path, format="wav")
    print(f"Converted {mp3_file_path} to {wav_file_path}")


def transcribe_audio_file(wav_file_path, language):
    if not os.path.exists(wav_file_path):
        print(f"Error: The file {wav_file_path} does not exist.")
        return
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_file_path) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data, language=language)
        print(f"Transcription: {text}")
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
