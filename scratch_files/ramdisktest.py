import tempfile

def foreign_language(source, file_extension):
    with tempfile.NamedTemporaryFile(suffix=file_extension) as _file:
        _file.write(source)
        _file.flush()
        subprocess.Popen(_file.name)
    
def create_ramdisk(directory, filesystem):
    format_args = (directory, file_system, directory, file_system)
    foreign_language("mkdir /tmp/ramdisk0 && mke2fs /dev/ram0 && mount /dev/ram0 /tmp/ramdisk0".format(*format_args)
        
        