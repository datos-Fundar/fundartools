from setuptools import setup, find_packages

setup(
   version="1.0.5",
   name="fundar",
   author="Fundar",
   description="Private Python library.",
   packages=find_packages(),
   package_data={'fundar': ['py.typed', '*.pyi', '**/*.pyi']},
   include_package_data=True,
   python_requires='>=3.10',
   setup_requires=['setuptools-git-versioning'],
   version_config={
       "dirty_template": "{tag}",
   }
)
