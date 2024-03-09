# Install Raspbian Bookworm on Organelle M

still incomplete

**Original instructions**  
[https://github.com/critterandguitari/Organelle_M_rootfs/blob/master/steps.md](url)

**PiGen** (Debian Buster only)  
[https://github.com/mogenson/organelle-m-pi-gen](url)

**Notes**   
Kernel 6.6.18:
- udev rules for gpiomem need to be changes --> added to Organelle_OS rootfs overlay

**64-bit**   
- externals in patches not compatible
- deken externals for aarch64 not available
- wiringPi doesn't work properly because of missing "Hardware" line in /proc/cpuinfo --> fixed in forked repo
- OG externals are compiled for 32bit --> some can be manually recompiled from [https://github.com/critterandguitari/Organelle_Externals](url), others still open (but not important)


## SD card creation
- create SD card with rpi-imager
- resize partition 2 (fdisk on Linux PC)
- create partition 3


## Basic setup
```
sudo apt update
sudo apt upgrade

sudo passwd root
	music

sudo raspi-config
```
- enable WLAN
- console auto-login
- enable VNC
- enable SPI
- enable I2C
- disable serial login
- enable serial interface

```
sudo apt install git
git config --global user.email "mxs@gmx.de"
git config --global user.name "steinmannm"

sudo rpi-update
sudo reboot
```

## Fix WM8731 driver
Make sure to use a kernel source version matching to the installed kernel.   
git --branch / git checkout ... needs to be adapted accordingly.

### Compile the missing kernel module wm8731-spi  
[https://www.raspberrypi.com/documentation/computers/linux_kernel.html](url)

```
sudo apt install git bc bison flex libssl-dev make libncurses-dev
mkdir src
cd src
git clone --depth=1 --branch rpi-6.6.y https://github.com/raspberrypi/linux
cd linux

```
for 32-bit kernel:
```
KERNEL=kernel7
make bcm2709_defconfig
```
for 64-bit kernel: 
```
KERNEL=kernel8
make bcm2711_defconfig
```
```
sed -i '/# CONFIG_SND_SOC_WM8731_SPI is not set/c\CONFIG_SND_SOC_WM8731_SPI=m' .config
make -j4 prepare
make -j4 modules_prepare
make -j4 -C /home/music/src/linux M=/home/music/src/linux/sound/soc/codecs KBUILD_MODPOST_WARN=1
sudo make -C /home/music/src/linux M=/home/music/src/linux/sound/soc/codecs modules_install
sudo depmod -A
kernelversion=$(make kernelversion)
```


### Patch snd-soc-audioinjector-pi-soundcard.ko.xz
```
cd ~/src
git clone https://github.com/critterandguitari/Organelle_M_rootfs.git
```
for 32-bit kernel:
```
cd /lib/modules/$kernelversion-v7+/kernel/sound/soc/bcm
```
for 64-bit kernel: 
```
cd /lib/modules/$kernelversion-v8+/kernel/sound/soc/bcm
```
```
sudo unxz snd-soc-audioinjector-pi-soundcard.ko.xz
sudo ~/src/Organelle_M_rootfs/audio/fixit.sh ./snd-soc-audioinjector-pi-soundcard.ko
sudo xz snd-soc-audioinjector-pi-soundcard.ko
```

### Install device tree overlay
```
sudo cp ~/src/Organelle_M_rootfs/audio/audioinjector-wm8731-audio-spi-overlay.dts /boot
sudo dtc -@ -I dts -O dtb -o /boot/overlays/wm8731-spi.dtbo /boot/audioinjector-wm8731-audio-spi-overlay.dts
```

### Disable automatic kernel updates (unconfirmed)
```
sudo apt-mark hold raspberrypi-bootloader raspberrypi-kernel raspberrypi-kernel-headers
```

### Edit config.txt
```
sudo nano /boot/config.txt
```
comment out:  
```
#dtparam=audio=on`
#dtoverlay=vc4-kms-v3d
```
uncomment:
```
dtparam=i2c_arm=on
dtparam=spi=on
disable_overscan=1
```
add:
```
enable_uart=1
dtoverlay=wm8731-spi
dtoverlay=gpio-poweroff,gpiopin=12,active_low="y"
dtoverlay=pi3-miniuart-bt
dtoverlay=midi-uart0 
dtoverlay=pi3-act-led,gpio=24,activelow=on
hdmi_force_hotplug=1
gpu_mem=64
```

### Set up ALSA mixer and test audio output
```
sudo reboot
alsamixer
```
- master = 0dB
- Master Playback on
- Sidetone off
- Mic boost 20dB
- Input Mux Line in
- Output Mixer on
```
speaker-test
   (doesn't work here with internal speaker yet)
```

## Installation of packages
```
sudo apt install zip jwm xinit x11-utils x11-xserver-utils lxterminal pcmanfm adwaita-icon-theme gnome-themes-extra gtk-theme-switch conky libasound2-dev liblo-dev liblo-tools python3-liblo python3-pip mpg123 dnsmasq hostapd cython3 iptables python3-cherrypy3 wish jackd2 luarocks csound supercollider nodejs

cd ~/src
git clone https://github.com/steinmannm/WiringPi
cd WiringPi
sudo ./build
```

## Install PD
```
sudo apt install autoconf gettext libfftw3-dev libjack-jackd2-dev libtool
cd ~/src
git clone https://github.com/pure-data/pure-data
cd pure-data
git checkout 0.54-1
./autogen.sh
./configure --enable-jack --enable-fftw --prefix /usr
make -j4
sudo make install
```

## Setup
```
sudo chmod +xr /root
sudo mkdir /sdcard
sudo chown music:music /sdcard
sudo mkdir /usbdrive
sudo chown music:music /usbdrive

cd /sdcard/
rm -fr Patches/
git clone https://github.com/critterandguitari/Organelle_Patches.git
mv Organelle_Patches/ Patches/
rm -fr Patches/.git
rm -fr Patches/.gitignore 
rm -fr Patches/README.md 

sudo visudo
    music ALL=(ALL) NOPASSWD: ALL

sudo mkfs.ext4 /dev/mmcblk0p3
sudo nano /etc/fstab
    /dev/mmcblk0p3 /sdcard  ext4 defaults,noatime 0 0

sudo reboot
sudo chown music:music /sdcard 

sudo nano /etc/security/limits.conf
    @music - rtprio 99
    @music - memlock unlimited
    @music - nice -10

sudo nano /etc/systemd/system.conf
    DefaultTimeoutStartSec=10s
    DefaultTimeoutStopSec=5s

sudo systemctl daemon-reload
```

## Deploy Organelle_OS
```
cd
git clone https://github.com/steinmannm/Organelle_OS
cd Organelle_OS/
git checkout bookworm
make organelle_m
sudo make organelle_m_deploy
cd
ln -s fw_dir/scripts/ scripts

sudo sh -c "echo '/opt/vc/lib' > /etc/ld.so.conf.d/00-vmcs.conf"
sudo ldconfig
```
Disable services
```
sudo systemctl disable cups.service cups-browsed.service
sudo systemctl disable vncserver-x11-serviced.service
```

in vncserver terminal: 
```
gtk-theme-switch2 /usr/share/themes/Adwaita
```

fix circle icon not showing up in Pd (tcl/tk doesn't like the adwaita circle icon for some reason, so just rename it to force fallback)
```
sudo mv /usr/share/icons/Adwaita/cursors/circle /usr/share/icons/Adwaita/cursors/circleORIG
```

---

## Additional packages


### ELSE library
```
cd ~/src
git clone https://github.com/porres/pd-else
git clone https://github.com/pure-data/pd-lib-builder
cd pd-else/
git checkout v.1.0-rc11
<fix sfz and sfont chdir bug>
make install objectsdir=~/Pd/externals
sudo apt install cmake
make -j4 sfz-install plaits-install objectsdir=~/Pd/externals

cd ~/src
git clone https://github.com/FluidSynth/fluidsynth
cd fluidsynth
git checkout v2.3.4
sudo apt install cmake libglib2.0-dev libsndfile1-dev patchelf
mkdir build
cd build
cmake -Denable-libsndfile=on -Denable-jack=off -Denable-alsa=off -Denable-oss=off -Denable-pulseaudio=off -Denable-ladspa=off -Denable-aufile=off -Denable-network=off -Denable-ipv6=off -Denable-getopt=off -Denable-sdl2=off -Denable-threads=off ..
sudo make -j4 install
sudo ldconfig

cd ~/src/pd-else/Code_source/Compiled/audio/sfont~
make PDLIBDIR=$HOME/Pd/externals install
make PDLIBDIR=$HOME/Pd/externals localdep_linux
mv ~/Pd/externals/sfont~/* ~/Pd/externals/else
rm -r sfont~/
```

### Jack clients
```
sudo apt install setbfree jalv mda-lv2 zynaddsubfx
```



## Optional: Install wlan driver for RTL8723BU (Edimax EW-7611ULB)
Install Kernel Headers for future module compilation
```
copy kernel sources to /usr/src/linux-headers-....
ln -s /lib/modules/version..../build  to /usr/src/......

```
follow [https://github.com/lwfinger/rtl8723bu](url)


## Optional: Bluetooth MIDI
[https://neuma.studio/raspberry-pi-as-usb-bluetooth-midi-host/](url)

### Bluetooth LE (not recommended, no security)
```
cd ~/src
git clone https://github.com/oxesoft/bluez
sudo apt-get install -y libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev
cd bluez
./bootstrap
./configure --enable-midi --prefix=/usr --mandir=/usr/share/man --sysconfdir=/etc --localstatedir=/var
make
sudo make install

```

### Bluetooth
```
sudo apt install pi-bluetooth
bluetoothctl
```
when a device is connected, an ALSA MIDI port becomes available 



## To Do

```
config

fix sort order. enable en_US.UTF8 in /etc/locale.gen, then
sudo locale-gen





release
check for default ap.txt and wifi.txt
check Patches folder looks good
clean up /sdcard
remove .viminfo
remove git config
clear command history:
cat /dev/null > ~/.bash_history && history -c && exit


sudo systemctl disable hciuart.service
systemctl disable dnsmasq.service
systemctl disable hostapd.service
systemctl disable dhcpcd.service
systemctl disable wpa_supplicant.service




make it read only
clean up
apt-get autoremove --purge

add to /boot/cmdline.txt
fastboot noswap ro

remove fsck.repair=yes, add fsck.mode=skip
move /var/spool to /tmp
rm -rf /var/spool
ln -s /tmp /var/spool

in /etc/ssh/sshd_config
UsePrivilegeSeparation no

in /usr/lib/tmpfiles.d/var.conf replace "spool 0755" with "spool 1777"
move dhcpd.resolv.conf to tmpfs
touch /tmp/dhcpcd.resolv.conf
rm /etc/resolv.conf
ln -s /tmp/dhcpcd.resolv.conf /etc/resolv.conf

in /etc/fstab add "ro" to /boot and /, then add:
tmpfs /var/log tmpfs nodev,nosuid 0 0
tmpfs /var/tmp tmpfs nodev,nosuid 0 0
tmpfs /tmp     tmpfs nodev,nosuid 0 0
--> find solution for /var/lib/bluetooth


stop time sync cause it is not working anyway. (also causes issues with LINK when the clock changes abruptly). need solution
timedatectl set-ntp false

reboot

release
pull latest Organelle_OS and deploy
remove .viminfo
remove git config
clear command history
run fsck
reboot and test
```