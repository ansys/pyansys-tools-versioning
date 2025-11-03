Getting started
###############

Installation
============

This package may be installed following two procedures: either the pip package
manager installation or the manual installation. The process to be followed for
each of them is shown in the upcoming sections.

The ``pyansys-tools-versioning`` package currently supports Python >=3.10 on
Windows, macOS, and Linux.

Install the latest release from PyPi with:

.. code-block:: bash

   python -m pip install pyansys-tools-versioning

Alternatively, install the latest from GitHub via:

.. code-block:: bash

   python -m pip install git+https://github.com/ansys/pyansys-tools-versioning.git

For a local development version, install with (requires pip >= 22.0):

.. code-block:: bash

   git clone https://github.com/ansys/pyansys-tools-versioning.git
   cd pyansys-tools-versioning
   python -m pip install -e .


Offline installation
====================
If you lack an internet connection in your local machine, the recommended way of
installing ``pyansys-tools-versioning`` is downloading the wheelhouse archive
from the Releases Page for your corresponding machine architecture.

Each wheelhouse archive contains all the python wheels necessary to install
PyAnsys Tools Report from scratch on Windows and Linux for Python >=3.10. You can
install this on an isolated system with a fresh python or on a virtual
environment.

For example, on Linux with Python 3.10, unzip it and install it with the
following:

.. code-block:: bash

   unzip pyansys-tools-versioning-v<major.minor.patch>-wheelhouse-Linux-3.10.zip wheelhouse
   python -m pip install pyansys-tools-versioning -f wheelhouse --no-index --upgrade --ignore-installed

If you are on Windows with Python 3.10, unzip to a wheelhouse directory and
install using the same command as before.

Consider installing using a virtual environment. More information on general
PyAnsys development can be found in the PyAnsys Developer's Guide.
