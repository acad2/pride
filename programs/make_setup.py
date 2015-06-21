import setuptools

import mpre.base

class Version_Manager(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    
options = {"name" : "mpre",
           "version" : ".5.9.21",
           "description" : "A dynamic runtime environment with a simple concurrency model",
           "url" : "https://github.com/erose1337/Metapython",
           "author" : "Ella Rose",
           "author_email" : "erose1337@hotmail.com",
           "packages" : ["mpre", "mpre.audio", "mpre.gui", "mpre.misc", "mpre.programs"]}
           
def setup(**kwargs):
    setuptools.setup(**kwargs)
    
if __name__ == "__main__":
    import mpre.fileio
    with mpre.fileio.current_working_directory(".."):
        setup(**options)