""" Builds the metapython runtime environment package """
import importlib
import sys
import setuptools

import pride.base
import pride.package
import pride.contextmanagers

class Version_Manager(pride.base.Base):
    
    defaults = pride.base.Base.defaults.copy()
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
        module = importlib.import_module(self.name)
        package = pride.package.Package(module, include_documentation=True)
        
        with pride.contextmanagers.current_working_directory(self.setuppy_directory):
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
        
        
with open("readme.md", 'r') as _file:
    long_description = _file.read()
    
options = {"name" : "pride",
           "version" : "5.9.43",
           "description" : "Python runtime and integrated development environment",
           "long_description" : long_description,
           "url" : "https://github.com/erose1337/pride",
           "download_url" : "https://github.com/erose1337/pride/archive/master.zip",
           "author" : "Ella Rose",
           "author_email" : "erose1337@hotmail.com",
           "packages" : ["pride", "pride.audio", "pride.gui", "pride.programs"],
           "scripts" : ["main.py"],
           "package_data" : {"pride.gui" : ["gui\\libfreetype-6.dll", 
                                            "gui\\SDL2.dll", "gui\\SDL2_ttf.dll",
                                            "gui\\sdlgfx.dll", "gui\\zlib1.dll",
                                            "gui\\sdlgfx.lib"],
           "classifiers" : ["Development Status :: 3 - Alpha", 
                            "Framework :: Pride", "Intended Audience :: Developers",
                            "Intended Audience :: End Users/Desktop",
                            "Operating System :: Microsoft :: Windows",
                            "Operating System :: POSIX :: Linux",
                            "Programming Language :: Python :: 2.7",
                            "Topic :: Desktop Environment", "Topic :: Documentation",
                            "Topic :: Games/Entertainment", "Topic :: Multimedia :: Sound/Audio",
                            "Topic :: Software Development :: Compilers", 
                            "Topic :: Software Development :: Code Generators",
                            "Topic :: Software Development :: Build Tools",
                            "Topic :: Software Development :: Libraries :: Application Frameworks",
                            "Topic :: Software Development :: Libraries :: Python Modules",
                            "Topic :: Software Development :: Pre-processors",
                            "Topic :: Software Development :: User Interfaces",
                            "Topic :: Software Development :: Widget Sets",
                            "Topic :: System :: Distributed Computing",
                            "Topic :: System :: Shells", 
                            "Topic :: Text Editors :: Integrated Development Environments (IDE)"]
                            }
           
try:           
    with open("Version_Manager.sav", 'rb') as saved_file:
        # for pickle reasons it doesn't work if this isn't done
        sys.modules["__main__"].Version_Manager = Version_Manager
        version_manager = pride.base.load(_file=saved_file)
except IOError:
    version_manager = Version_Manager(**options)    
        
if __name__ == "__main__":
    version_manager.run_setup()
    with open("Version_Manager.sav", 'wb') as saved_file:
        version_manager.save(_file=saved_file)