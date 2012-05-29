# Setup 

As a superuser set a default route to the interface where the switch is connected:

##Example:

    ip route add 255.255.255.255 dev eth1

If your interface is **not** eth0 please specify it, when you call *psl-cmd.py*.

##Example:

    ./psl-cmd.py --interface eth1 discover

# DEPENDENCYS


http://code.google.com/p/ipaddr-py/downloads/detail?name=3144.tar.gz