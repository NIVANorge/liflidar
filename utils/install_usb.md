To make a seabreeze working:
1. use `lsusb` to check idVendor and idProduct of a necessary usb, 
we are looking for a Ocean Optics device:
"Bus 001 Device 004: ID 2457:4000 Ocean Optics Inc. STS"
here: 2457 - idVendor; 4000 - idProduct 
2. Add a rule 
SUBSYSTEM=="usb", ATTRS{idVendor}=="2457", ATTRS{idProduct}=="4000", GROUP="plugdev", MODE="0660"
to file `/etc/udev/rules.d/50-usb-perms.rules`.
See the example file in the current folder.
3. then run:
```
sudo udevadm control --reload
sudo udevadm trigger
```

some more info: the usb device files are in `/dev/bus/usb/`;
use lsusb to check the location of a particular device.

check the device file permissions, plugdev should have the access to it:
```
pi@phox:~ $ ls -l /dev/bus/usb/001/004
crw-rw---- 1 root plugdev 189, 3 Oct 24 12:26 /dev/bus/usb/001/004
```

`groups pi` command will should the user groups

