mpre.makepackage
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
- deleted                  False
- verbosity                vv
- ignore_directories       ('docs',)
- subfolders               ()
- memory_size              4096
- ignore_files             ('build_documentation.py',)
- directory                C:\Users\_\pythonbs\mpre
- index_page               ('index.md', 'Homepage')

This object defines the following non-private methods:


- **write_yml_file**(self, file_data):

		  No documentation available



- **update**(self):

		  No documentation available



- **generate_md_file**(self, module_name):

		  Generates an .md file from a python module


This objects method resolution order is:

(class 'mpre.makepackage.Documentation', class 'mpre.base.Base', type 'object')


Package
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- directory                None
- subfolders               ()
- memory_size              4096
- package_name             None
- deleted                  False
- verbosity                

This object defines the following non-private methods:


- **update_structure**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.makepackage.Package', class 'mpre.base.Base', type 'object')
