# -*- coding: utf-8 -*-
#
# This file is part of Lifewatch DAAP.
# Copyright (C) 2015 Ana Yaiza Rodriguez Marrero.
#
# Lifewatch DAAP is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lifewatch DAAP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lifewatch DAAP. If not, see <http://www.gnu.org/licenses/>.

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
