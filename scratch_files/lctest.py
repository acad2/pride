def get_line_count(filename, ignore_comments=True):
    comments = physical_count = 0    
    with open(filename, 'r') as _file:
        for line in _file.readlines():
            _line = line.strip()
            if _line and _line[0] == '#':
                comments += 1
            physical_count += 1
    return physical_count - (comments if ignore_comments else 0)
    
#def get_project_line_count(directory):
    
    
       
if __name__ == "__main__":
    print get_line_count("base.py")