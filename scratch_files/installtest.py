try:
    import cPickle as pickle
except:
    import pickle

class Installer(object):
    
    def __init__(self, package_filename, install_directory=None):
        super(Installer, self).__init__()
        self.package_filename = package_filename
        self.install_directory = install_directory
        
    def install(self):
        with open(self.package_filename, 'r') as package_file:
            package = pickle.load(package_file)
            package_file.close()
       
        if self.install_directory is not None:
            package.directory = self.install_directory
        
        package.update_structure()
        
if __name__ == "__main__":
    installer = Installer("pride.pyp", '')
    installer.install()