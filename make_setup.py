import sys
import setuptools

import mpre.base

class Version_Manager(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"name" : '',
                     "version" : '',
                     "description" : '',
                     "url" : '',
                     "author" : '',
                     "author_email" : '',
                     "packages" : '',
                     "setuppy_directory" : '..',
                     "options" : ("name", "version", "description",
                                  "url", "author", "author_email", "packages")})    
    def _get_options(self):
        return dict((attribute, getattr(self, attribute)) for 
                     attribute in self._options)
    def _set_options(self, values):
        self._options = values
    options = property(_get_options, _set_options)
    
    def run_setup(self, argv="sdist"):
        with mpre.fileio.current_working_directory(self.setuppy_directory):
            backup = sys.argv
            sys.argv = [backup[0], argv]
            setuptools.setup(**self.options)
            sys.argv = backup
        self.increment_version()
                
    def increment_version(self, amount="0.0.1"):
        # There has got to be a nicer way of adding integers represented as strings
        current_version = self.version.split('.')
        while '' in current_version:
            location = current_version.index('')
            current_version.pop(location)
            current_version.insert(location, 0)
            
        current_version = [int(item) for item in reversed(current_version)]   
        amount = amount.split(".")
        while '' in amount:
            location = amount.index('')
            amount.pop(location)
            amount.insert(location, 0)
            
        amount = [int(item) for item in reversed(amount)]
        carry = 0
        new_versions = []

        for index, quantity in enumerate(amount):
            new_version = quantity + current_version[index] + carry
            carry, new_version = divmod(new_version, 100)
            new_versions.append(str(new_version))
        self.version = '.'.join(reversed(new_versions))
            
options = {"name" : "mpre",
           "version" : ".5.9.21",
           "description" : "A dynamic runtime environment with a simple concurrency model",
           "url" : "https://github.com/erose1337/Metapython",
           "author" : "Ella Rose",
           "author_email" : "erose1337@hotmail.com",
           "packages" : ["mpre", "mpre.audio", "mpre.gui", "mpre.misc", "mpre.programs"]}
           
try:           
    with open("Version_Manager.sav", 'rb') as saved_file:
        version_manager = mpre.base.load(_file=saved_file)
except IOError:
    version_manager = Version_Manager(**options)    
        
if __name__ == "__main__":
    version_manager.run_setup()
    with open("Version_Manager.sav", 'wb') as saved_file:
        version_manager.save(_file=saved_file)