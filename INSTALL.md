2016-ABAPlus: Modules that perform computations related to ABA+
===============================================================

Prerequisites
=============
* Required: Python 3
* Required: pip3
* Required: Python module numpy
* Required: Python module django
* Required: clingo 4.5.4
* Required: DLV version December 17th, 2012 (for ideal semantics)

## Ubuntu 14.04 (64 bit), 16.04 (64 bit) and 16.10 (64 bit)
Python 3 is already installed as `python3`.
The dlv executable for Linux 64-bit is already in the 2016-ABAPlus root directory.

To install pip3, in a terminal enter:

    sudo apt-get install python3-pip

To install numpy and django, in a terminal enter:

    sudo pip3 install numpy django

To install clingo, download 
https://sourceforge.net/projects/potassco/files/clingo/4.5.4/clingo-4.5.4-source.tar.gz/download .
In a terminal, change to the directory where you downloaded it and enter the following.
(The sed statement fixes a bug in term.cc by inserting the line `#include <cmath>`.)

    sudo apt-get install build-essential scons bison re2c
    tar xvfz clingo-4.5.4-source.tar.gz
    cd clingo-4.5.4-source
    sed -i '1 i\#include <cmath>' libgringo/src/term.cc
    scons --build-dir=release
    

## OS X 10.10, OS X 10.11 and macOS 10.12

To install Python 3 and pip3, install MacPorts from
http://www.macports.org/install.php . In a new terminal, enter:

    sudo port install python35 py35-pip
    sudo port select --set python3 python35
    sudo port select --set pip pip35

To install numpy and django, in a terminal enter:

    sudo pip install numpy django

To install clingo, download
https://sourceforge.net/projects/potassco/files/clingo/4.5.4/clingo-4.5.4-source.tar.gz/download .
In a terminal, change to the directory where you downloaded it and enter the following.

    sudo port install scons bison re2c
    tar xvfz clingo-4.5.4-source.tar.gz
    cd clingo-4.5.4-source
    scons --build-dir=release

To install DLV, download
http://www.dlvsystem.com/files/dlv.i386-apple-darwin.bin . We need to move this from the
download folder and replace the Linux executable. In a terminal, 
change directory to the 2016-ABAPlus root and enter:

    mv <download folder>/dlv.i386-apple-darwin.bin dlv
    chmod a+x dlv

Build
=====
You need ABAPlus on the Python path.  To temporarily set it, do the following.
If `<ABAPlus root>` is the path to the root of the 2016-ABAPlus distribution, in a terminal enter:

    export PYTHONPATH=$PYTHONPATH:<ABAPlus root>

You need clingo on the PATH. If `<clingo root>` is the folder of the uncompressed clingo distribution,
either add `<clingo root>/build/release` to the PATH in your shell startup script, or simply enter:

    export PATH=$PATH:<clingo root>/build/release

To run the unit tests, in a terminal change to the directory `<ABAPlus root>` and enter:

    python3 -m unittest

The unit tests should print a bunch of dots and a message like "Ran 47 tests in 0.113s".
If not, then there could be something wrong with your installation.

One time only, you need to apply migrations for your Django installation. In a terminal, enter:

    python3 manage.py migrate

To run the Django web server, in a terminal enter:

    python3 manage.py runserver

It should print some messages including something like "Starting development server at http://127.0.0.1:8000/".
Copy the address http://127.0.0.1:8000 and paste it into a web browser. You should see the ABA+ page.
