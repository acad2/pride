from setuptools import setup

setup(name="Metaprogramming Framework",
      description="An asynchronous embeddable virtual machine, capable of running an arbitrary number of framework processes concurrently.",
      long_description=open("documentation/docs/index.md", "r").read(),
      classifiers=["Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License (GPL)"
        "Programming Language :: Python :: 2.7",
        "Intended Audience :: Developers",
        "Topic :: System :: Shells",
        "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Other/Nonlisted Topic"],
        #"Topic :: Software Development :: User Interfaces" # with from pygame to pysdl
        #Topic :: System :: Distributed Computing # some day!       
      keywords="concurrency asynchronous virtual machine",
      url="https://github.com/erose1337/Metaprogramming_Framework",
      author="Ella Rose",
      author_email="erose1337@hotmail.com",
      license="GNU GPL",
      packages=["audio", "documentation", "framework", "utilities", "programs"],
      include_package_data=True,
      zip_safe=True)