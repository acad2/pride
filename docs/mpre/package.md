mpre.package
========
No documentation available

Documentation
--------
	
	Generates restructed text .md files from python modules.
	Writes a mkdocs.yml with the .md files information.
	Runs mkdocs build to build a site from the .md files
	

Default values for newly created instances:

- network_packet_size      4096
- site_name                
- package                  None
- deleted                  False
- verbosity                vv
- ignore_directories       ('docs',)
- subfolders               ()
- memory_size              4096
- ignore_files             ('build_documentation.py',)
- directory                C:\Users\_\pythonbs\mpre
- index_page               ()

This object defines the following non-private methods:


- **write_yml_file**(self, file_data):

		  No documentation available



- **update**(self):

		  No documentation available



- **generate_md_file**(self, module_name):

		  Generates an .md file from a python module


This objects method resolution order is:

(class 'mpre.package.Documentation', class 'mpre.base.Base', type 'object')


Package
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- package_name             
- make_docs                True
- deleted                  False
- verbosity                
- store_source             True
- subfolders               ()
- memory_size              4096
- directory                

This object defines the following non-private methods:


- **update_structure**(self):

		  No documentation available



- **init_filename_in**(self, path):

		  No documentation available



- **make_files**(self, subfolder, subpath, file_list):

		  No documentation available



- **make_folder**(self, subfolder, folder_path):

		  No documentation available



- **from_directory**(top_directory, dirnames):

		  No documentation available


This objects method resolution order is:

(class 'mpre.package.Package', class 'mpre.base.Base', type 'object')
