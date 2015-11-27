if __name__ == "__main__":
    with open("inlinetest3.py", 'r') as _file:
        source = _file.read()
    from importers import Preprocess_Decorator
    p = Preprocess_Decorator()
    print p.handle_source(source)