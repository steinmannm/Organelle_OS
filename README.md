# Install Raspbian Bookworm on Organelle M

still incomplete

**Manual**  
[https://github.com/critterandguitari/Organelle_M_rootfs/blob/master/steps.md](url)

**PiGen** (works for Buster only)  
[https://github.com/mogenson/organelle-m-pi-gen](url)


## SD card creation
- create SD card with rpi-imager
- resize partition 2 (fdisk on Linux PC)
- create partition 3


## Basic setup
```
sudo raspi-config
```
- enable WLAN
- enable VNC
- console auto-login
- enable SPI
- enable I2C
- disable serial login
- enable serial interface

```
sudo apt update
sudo apt upgrade
sudo passwd root
	music

sudo apt install git
git config --global user.email "mxs@gmx.de"
git config --global user.name "steinmannm"

sudo rpi-update
sudo reboot
```

## Fix WM8731 driver
Make sure to use a kernel source version matching to the installed kernel.   
git --branch ... and module paths need to be adapted accordingly.

### Compile the missing kernel module wm8731-spi  
[https://www.raspberrypi.com/documentation/computers/linux_kernel.html](url)

```
sudo apt install git bc bison flex libssl-dev make libncurses-dev
mkdir src
cd src
git clone --depth=1 --branch rpi-6.6.y https://github.com/raspberrypi/linux
cd linux
KERNEL=kernel7
make bcm2709_defconfig
sed -i '/# CONFIG_SND_SOC_WM8731_SPI is not set/c\CONFIG_SND_SOC_WM8731_SPI=m' .config
make -j4 prepare
make -j4 modules_prepare
make -j4 -C /home/music/src/linux M=/home/music/src/linux/sound/soc/codecs KBUILD_MODPOST_WARN=1
sudo make -C /home/music/src/linux M=/home/music/src/linux/sound/soc/codecs modules_install
sudo depmod -A
```

### Patch snd-soc-audioinjector-pi-soundcard.ko.xz
```
git clone https://github.com/critterandguitari/Organelle_M_rootfs.git
cd /lib/modules/6.6.16-v7+/kernel/sound/soc/bcm
sudo unxz snd-soc-audioinjector-pi-soundcard.ko.xz
sudo ~/Organelle_M_rootfs/audio/fixit.sh ./snd-soc-audioinjector-pi-soundcard.ko
sudo xz snd-soc-audioinjector-pi-soundcard.ko
```

### Install device tree overlay
```
sudo cp ~/Organelle_M_rootfs/audio/audioinjector-wm8731-audio-spi-overlay.dts /boot
sudo dtc -@ -I dts -O dtb -o /boot/overlays/wm8731-spi.dtbo /boot/audioinjector-wm8731-audio-spi-overlay.dts
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
- Sidetone 
- Mic boost 20dB
- Input Mux Line in
- Output Mixer on
```
speaker-test
```

## Installation of packages
```
sudo apt install zip jwm xinit x11-utils x11-xserver-utils lxterminal pcmanfm adwaita-icon-theme gnome-themes-extra gtk-theme-switch conky libasound2-dev liblo-dev liblo-tools python3-liblo python3-pip mpg123 dnsmasq hostapd cython3 iptables python3-cherrypy3 wish jackd2 luarocks csound supercollider nodejs

cd ~/src
git clone https://github.com/WiringPi/WiringPi
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
in vncserver terminal: 
```
gtk-theme-switch2 /usr/share/themes/Adwaita
```

Disable services
```
sudo systemctl disable cups.service cups-browsed.service
```
---


## Additional stuff
'''
sudo apt install 




## To Do

```
config
fix circle icon not showing up in Pd (tcl/tk doesn't like the adwaita circle icon for some reason, so just rename it to force fallback)
sudo mv /usr/share/icons/Adwaita/cursors/circle /usr/share/icons/Adwaita/cursors/circleORIG

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
sudo systemctl disable vncserver-x11-serviced.service
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