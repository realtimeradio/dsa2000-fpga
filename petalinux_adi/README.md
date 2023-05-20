# Building Linux for iWave SoM

1. Make sure you have initialized and updated the `meta-adi` git submodule
2. Download and install [petalinux 2021.2](https://www.xilinx.com/support/download/index.html/content/xilinx/en/downloadNav/embedded-design-tools.html)
3. Set up petalinux environment: `source <path-to-petalinux>/settings.sh`
4. Create new petalinux project: `petalinux-create -t project --template zynqMP --name adijesd`
5. Copy config `cp petalinuxbsp.conf adijesd/project-spec/meta-user/conf/`
6. Set path to `xsa` file for pre-exported Vivado project. Eg:
```
export XSA_DIR=/home/jackh/src/dsa2000-fpga/firmware/src/models/dsa2k_iwave_adc_only/myproj
```
7. Enter project: `cd adijesd`
8. Configure project for target hardware -- `petalinux-config --get-hw-description=$XSA_DIR`
9. Add ADI Yocto layers in configuration GUI:
```
Yocto Settings ---> User Layers --->
user layer 0: <path_to_meta-adi>/meta-adi-core
user layer 1: <path_to_meta-adi>/meta-adi-xilinx
```
10. Set rootfs to build for SD card:
```
Image Packaging Configuration ---> Root filesystem type ---> EXT4
Image Packaging Configuration ---> Device node of SD device ---> /dev/mmcblk1p2
```
11. Add top-level device tree to Linux source. This is surely not the right way to use the tools, use `KERNEL_DTB_PATH` instead?
```
ln -s ../../../../../../../../../../../system-top.dts ./build/tmp/work-shared/zynqmp-generic/kernel-source/arch/arm64/boot/dts/xilinx/system-top.dts
```
12. Include custom device tree:
```
ln -s ../../../../../../system-user.dtsi project-spec/meta-user/recipes-bsp/device-tree/files/system-user.dtsi`
```
13. Build!
```
petalinux-build
```
14. Package:
```
# Use another FPGA image if you want, but be sure it is compatible with the .XSA used for this project!
petalinux-package --boot --fsbl images/linux/zynqmp_fsbl.elf --fpga images/linux/system.bit --u-boot --force
```
15. Copy the following to the boot partition of an SD card:
```
images/linux/BOOT.BIN
images/linux/boot.scr
images/linux/image.ub
```

