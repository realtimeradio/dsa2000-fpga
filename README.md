# dsa2000-fpga
A repository for DSA2000 F-engine FPGA firmware and control software.

## Software Versions:
- Ubuntu 18.04
- Xilinx Vivado System Edition 2021.2
- MATLAB/Simulink 2021a

## To open/modify/compile:

1. Clone this repository
2. Clone submodules:
```
git submodule update --init --recursive
```
3. Create a local environment specification file `firmware/startsg.local`.
4. Prior to compiling firmware, make ADI IP
```
cd firmware
source startsg
cd lib/adi_hdl/library
make all # Then get a coffee
```
5. From `firmware/`, run `startsg` (if your environment file is called `startsg.local`) or `startsg <my_local_environment_file.local>`.

## Repository Layout

 - `firmware/` -- Firmware source files and libraries
 - `software/` -- Libraries providing communication to FPGA hardware and firmware
 - `docs/` -- Documentation
