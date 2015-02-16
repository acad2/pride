import os
import cPickle as pickle

import mpre.package

options = {"verbosity" : "vvv"}   
                       
directory = options["directory"] = 'C:\\users\\_\\pythonbs'
package_name = options["package_name"] = "mpre"
subfolders = options["subfolders"] = ["programs", 'audio', "gui", "misc"]

if __name__ == "__main__":  
    files = mpre.package.Package.from_directory(os.path.join(directory,
                                                             package_name),
                                                subfolders)
    options["files"] = files
    package = mpre.package.Package(**options)
    with open("mpre.pyp", 'w') as package_file:
        pickle.dump(package, package_file)
        package_file.flush()
        package_file.close()
    print "complete!"