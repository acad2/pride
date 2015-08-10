import mpre.audio.audiolibrary
import mpre.audio.utilities

if __name__ == "__main__":
    mpre.audio.utilities.ensure_audio_enabled()
    mpre.audio.audiolibrary.record_wav_file(parse_args=True)