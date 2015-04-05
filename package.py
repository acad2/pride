import os
import importlib
import traceback
import contextlib

import mpre
import mpre.base as base
import mpre.defaults as defaults
import mpre.fileio as fileio
import mpre.utilities as utilities
ensure_file_exists = fileio.ensure_file_exists
ensure_folder_exists = fileio.ensure_folder_exists

@contextlib.contextmanager
def ignore_instructions():
    backup = mpre.environment.Instructions
    try:
        yield
    finally:
        mpre.environment.Instructions = backup
        

class Package(base.Base):
            
    defaults = defaults.Base.copy()
    defaults.update({"package_name" : '',
                     "subfolders" : tuple(),
                     "directory" : '',
                     "store_source" : True,
                     "make_docs" : True})
                     
    def __init__(self, **kwargs):
        self.files = {}
        self.file_source = {}
        super(Package, self).__init__(**kwargs)
        
        self.directory = self.directory if self.directory else os.getcwd()
        
        if not self.package_name:
            self.package_name = raw_input("Please provide the package name: ")
        self.update_structure()
        
        if self.make_docs:
            self.create(Documentation, package=self)
    
    def init_filename_in(self, path):
        return os.path.join(path, "__init__.py")
    
    @staticmethod
    def from_directory(top_directory, dirnames):  
        folder_paths = [(top_directory, os.path.split(top_directory)[-1])]
        for directory in os.listdir(top_directory):
            path = os.path.join(top_directory, directory)
            if os.path.isdir(path):
                folder_paths.append((path, directory))    
        
        file_package = {}            
        for full_path, folder in folder_paths:
            file_package[folder] = [os.path.join(full_path, _file) for _file in 
                                    os.listdir(full_path) if "_" != _file[0] and
                                    os.path.splitext(_file)[-1] == ".py"]
        return file_package 
    
    def update_structure(self):
        directory = self.directory
        package_name = self.package_name
        files = self.files
        
        folder_path = os.path.join(directory, self.package_name)
        self.alert("Creating folder structure", level='v')
        
        self.make_folder(package_name, folder_path)
        
        for subfolder in self.subfolders:
            print "Building subfolder", subfolder
            subpath = os.path.join(folder_path, subfolder)
            self.make_folder(subfolder, subpath)         
                    
        self.alert("Finished creating {} folder structure", [self.package_name], level='v')
  
    def make_folder(self, subfolder, folder_path):
        ensure_folder_exists(folder_path)
        ensure_file_exists(self.init_filename_in(folder_path))

        if subfolder in self.files:
            self.make_files(subfolder, folder_path, self.files[subfolder])
            
    def make_files(self, subfolder, subpath, file_list):
        new_info = []
        for file_info in file_list:
            try:
                filename, file_data = file_info
            except ValueError:
                if not os.path.exists(file_info):
                    print "path does not exist: ", file_info
                    assert os.path.exists(file_info)
                path, filename = os.path.split(file_info)
                
                with open(file_info, 'r') as source_file:
                    file_data = source_file.read()
                    source_file.close()                    

            ensure_file_exists(os.path.join(subpath, filename), data=file_data)
            
            if self.store_source:
                new_info.append((filename, file_data))
                
        if self.store_source:
            self.files[subfolder] = new_info

           
class Documentation(base.Base):
    """
    Generates restructed text .md files from python modules.
    Writes a mkdocs.yml with the .md files information.
    Runs mkdocs build to build a site from the .md files
    """    
    defaults = defaults.Base.copy()
    defaults.update({"directory" : os.getcwd(),
                     "subfolders" : tuple(),
                     "ignore_directories" : ("docs", ),
                     "ignore_files" : tuple(),
                     "site_name" : '',
                     "verbosity" : 'vv',
                     "index_page" : tuple(),
                     "package" : None})
                    
    def __init__(self, **kwargs):
        super(Documentation, self).__init__(**kwargs)
        if self.package:
            package = self.package
            package_name = self.site_name = package.package_name
            directory = self.directory = os.path.join(package.directory, package_name)
            os.chdir(self.directory)
            docs_directory = os.path.join(directory, "docs")
            ensure_folder_exists(docs_directory)
            ensure_file_exists(os.path.join(docs_directory, "index.md"),
                               data="{}\n{}".format(package_name, "="*15))
                  
        if not self.site_name:
            self.site_name = raw_input("Please enter site name: ")
        
        if not self.index_page:
            self.index_page = ["index.md", "Homepage"]
            
        self.update()
        
    def update(self):     
        directory = self.directory      
        
        subfolders = self.subfolders if self.subfolders\
                     else [name for name in os.listdir(directory) if 
                           name not in self.ignore_directories and
                           os.path.isdir(os.path.join(directory, name))]
                               
        subfolders.insert(0, directory)
        
        package_name = os.path.split(directory)[-1]             
        site_name = "site_name: {}\n".format(self.site_name)
        index_page = self.index_page
        page_entries = ''        
        page_section = "pages:\n"
        page_string = "- ['{}', '{}', '{}']\n"  
        
        md_files = []
        for subfolder in subfolders:
            dest_folder = subfolder if subfolder != directory else package_name
            subfolder_path = os.path.join(directory, subfolder)
            ensure_folder_exists(os.path.join(directory, "docs", dest_folder))
            
            self.alert("\nWorking on {}", [subfolder], 'v')
            
            py_files = (_file for _file in os.listdir(subfolder_path)
                        if _file not in self.ignore_files
                        and "_" != _file[0] # auto ignore private modules
                        and os.path.splitext(_file)[-1] == ".py")
                        
            for python_file in py_files:
                module_name, py_extension = os.path.splitext(python_file)
                md_filename = module_name + ".md"
                
                if subfolder == directory:
                    module_path = '.'.join((package_name, module_name))                    
                    md_filepath = os.path.join(directory, "docs", package_name, md_filename)
                else:
                    module_path = ".".join((package_name, subfolder, module_name))
                    md_filepath = os.path.join(directory, "docs", subfolder, md_filename)
                    
                self.alert("Importing {}", [module_path], 'vv')                
                try:
                    md_text = self.generate_md_file(module_path)
                except ImportError:
                    self.alert("Could not import {}. Could not create .md file\n{}",
                               [module_name, traceback.format_exc()],
                               0)
                    continue
                    
                with open(md_filepath, 'w') as md_file:
                    md_file.write(md_text)
                    md_file.flush()
                    md_file.close()
                
                self.alert("Created md file {}", [md_filepath], level='v')
                
                category_name = subfolder if subfolder != directory else package_name
                page_entries += page_string.format(os.path.join(category_name, md_filename),
                                                   category_name,  
                                                   module_name)
                                                   
            file_data = "{}{}- {}\n{}".format(site_name,
                                              page_section,
                                              index_page,
                                              page_entries)
        self.write_yml_file(file_data)
        utilities.shell("mkdocs build", shell=True)
        return file_data        
        
    def generate_md_file(self, module_name):
        """usage: documentation.generate_md_file(module_name) => documentation"""
        null_docstring = 'No documentation available'
        with ignore_instructions():
            try:
                module = importlib.import_module(module_name)
            except:
                print traceback.format_exc()
                documentation = null_docstring
            else:
                module_docstring = module.__doc__ if module.__doc__ else null_docstring
                    
                documentation = [''.join((module_name, "\n========\n", module_docstring))]
                _from = getattr(module, "__all__", dir(module))
                    
                for attribute in getattr(module, "__all__", dir(module)):
                    module_object = getattr(module, attribute)
                    if isinstance(module_object, type) and attribute[0] != "_":
                        docstring = module_object.__doc__ if module_object.__doc__ else null_docstring
                        documentation.append("\n" + ''.join((attribute, "\n--------\n", docstring)))
                            
        return "\n".join(documentation)
        
    def write_yml_file(self, file_data):
        with open("mkdocs.yml", "w") as yml_file:
            yml_file.write(file_data)
            yml_file.flush()
            yml_file.close()
        self.alert("\n{}", [file_data], level='v')
        
        
if __name__ == "__main__":
    subfolders = ["test1", "testagain", "lolcool"]
    files = {"testagain" : ["C:\\users\\_\\pythonbs\\mpre\\vmlibrary.py"]}
    test_package = Package(package_name="Test_Package",
                           subfolders=subfolders,
                           files=files)