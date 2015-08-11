import mpre.audio.audiolibrary

if __name__ == "__main__":
    mpre.audio.enable()
    mpre.audio.audiolibrary.record_wav_file(parse_args=True)