import os
import cPickle as pickle

import mpre.package

options = {"verbosity" : "vvv",
           "directory" : 'C:\\users\\_\\pythonbs',
           "package_name" : "mpre",
           'subfolders' : ["programs", "audio", "gui", "misc"]}
    
files = {"mpre" : ["base.py", "defaults.py", "keyboard.py",
                   "metapython.py", "networklibrary.py",
                   "networklibrary2.py", "package.py",
                   "shell_launcher.py", "stdin.py",
                   "utilities.py", "vmlibrary.py"],
         "programs" : ["stupidsend.py", "stupidreceive.py",
                       "send_file.py", "remote_connection.py",
                       "get_modules.py", "file_server.py",
                       "download_file.py", "create_package.py",
                       "compile.py", "bytecodemap.py",
                       "bytecodedis.py", "_compile.py"],
         "audio" : ["alsaaudiodevices.py", "audio_config_utility.py",
                    "audiolibrary.py", "capture_live_audio.py",
                    "defaults.py", "play_wav_file.py",
                    "portaudiodevices.py", "voipmessenger.py"],
         "gui" : ["defaults.py", "guilibrary.py", "sdllibrary.py",
                  "sdltest.py", "widgetlibrary.py", "sdlconstants.txt"],
         "misc" : ["verbosedialect.py", "securitylibrary.py", "mmaptest.py",
                   "downloadtest.py", "dialectlibrary.py", "decoratorlibrary.py",
                   "decoratorlibrary2.py", "convert_bases.py"]
        }

directory = options["directory"]
package_name = options["package_name"]
        
for key, filenames in files.items():
    if key == options["package_name"]:
        full_path = [os.path.join(directory, package_name, filename) for filename in filenames]
    else:
        full_path = [os.path.join(directory, package_name, key, filename)
                     for filename in filenames]
                     
    files[key] = full_path
    
options["files"] = files        
    
if __name__ == "__main__":
    package = mpre.package.Package(**options)
    with open("mpre.pyp", 'w') as package_file:
        pickle.dump(package, package_file)
        package_file.flush()
        package_file.close()
    print "complete!"