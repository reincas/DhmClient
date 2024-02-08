# HoloServer

This package contains a TCP/IP client for remote access to a digital holographic microscope from LyncéeTec written as Python 3 package. It also contains Python scripts to access the client via external commands of 3DPoliCompiler used to control the Laser Nanofactory from Femtika.


## Installation

To build and install the package, run the command

```
python -m pip install .
```

To clean all intermediate files and directories, run
```
python clean.py
```


## Usage examples

See Python scripts in the directory `test`.


## Generate new command set

Edit and run  `command_list.py`. Copy `dhmserver\Commands.cs` to the library `DhmServer` and recompile the server.