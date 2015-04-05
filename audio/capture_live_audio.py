import mpre.audio.utilities as utilities
if __name__ == "__main__":
    utilities.ensure_audio_enabled()
    utilities.record_wav_file(parse_args=True)