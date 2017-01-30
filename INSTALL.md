2016-ABAPlus: Modules that perform computations related to ABA+
===============================================================

Prerequisites
=============
* Required: Python 3
* Required: pip3
* Required: Python module numpy
* Required: Python module django
* Required: clingo 4.5.4

## Ubuntu 14.04, 16.04 and 16.10
Python 3 is already installed as `python3`.

To install pip3, in a terminal enter:

    sudo apt-get install python3-pip

To install numpy and django, in a terminal enter:

    sudo pip3 install numpy django

To install clingo, download `https://sourceforge.net/projects/potassco/files/clingo/4.5.4/clingo-4.5.4-source.tar.gz/download` .
In a terminal, change to the directory where you downloaded it and enter the following.
(The sed statement fixes a bug in term.cc by inserting the line `#include <cmath>`.)

    sudo apt-get install build-essential scons bison re2c
    tar xvfz clingo-4.5.4-source.tar.gz
    cd clingo-4.5.4-source
    sed -i '1 i\#include <cmath>' libgringo/src/term.cc
    scons --build-dir=release
    
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

