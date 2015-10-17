import pride.audio.audiolibrary

if __name__ == "__main__":
    pride.audio.enable()
    pride.audio.audiolibrary.record_wav_file(parse_args=True)