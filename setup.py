from setuptools import setup
from setuptools import setup, find_packages
packages = find_packages()

print packages

setup(
    name="ebd_portal",
    version="0.1",
    url="http://aeonium.eu/",
    author="aeonium",
    author_email="info@aeonium.eu",
    description="Open Data Portal EBD",
    packages=packages,
    install_requires=[
    	"Invenio>=2"
    ],
    entry_points={
        "invenio.config": ["ebd_portal = ebd_portal.config"]
    }
)
