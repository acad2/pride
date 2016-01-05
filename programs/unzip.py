import zipfile
import pride.base

class Unzipper(pride.base.Base):
    
    defaults = {"filename" : '', "target_directory" : ''}
    required_attributes = ("filename", )
                
    def __init__(self, **kwargs):
        super(Unzipper, self).__init__(**kwargs)
        with zipfile.ZipFile(self.filename, 'r') as zipped_file:
            if self.target_directory:
                zipped_file.extractall(self.target_directory)
            else:
                zipped_file.extractall()
                
if __name__ == "__main__":
    zip_file = Unzipper(parse_args=True)
    zip_file.unzip()