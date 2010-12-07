Compile SRILM 

For Ubuntu 10.04 64bit:

sudo apt-get install csh
edit sbin/machine type to uncomment 64bit architecture
make MAKE_PIC=yes World -j 2
