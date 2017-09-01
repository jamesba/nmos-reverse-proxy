# NMOS Reverse Proxy

This package includes the NMOS reverse proxy utility. This is used to present multiple APIs on the same machine listening on different ports on a single port. By default this is port 80.

The utility presents a top level directory structure, under which each of the APIs has a path as per the NMOS conventions for APIs.

## Debian packaging

This utility depends on the [nmos-common](https://github.com/bbc/nmos-common). Please make sure this has been installed before proceeding.

This package is only suitable for use with Debian systems, and as such has been debian packaged.
To install:

```
apt-get install devscripts apache2-dev debhelper -y
make deb
dpkg -i reverse-proxy_*_all.deb
sudo apt-get -f -y install
```
