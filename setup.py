from setuptools import setup
from setuptools import setup, find_packages
packages = find_packages()

print packages

setup(
    name="lw_daap",
    version="0.1",
    url="http://aeonium.eu/",
    author="aeonium",
    author_email="info@aeonium.eu",
    description="LifeWatch Data Access and Preservation",
    packages=packages,
    install_requires=[
    	"Invenio>=2"
    ],
    entry_points={
        "invenio.config": ["lw_daap = lw_daap.config"],
        'console_scripts': [
            # overwrite invenio bibupload
            'bibupload = lw_daap.ext.bibupload.scripts.bibupload:main',
        ],
    }
)
