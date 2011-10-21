#!/bin/bash
echo "Building cortex-client from trunk"

cd `dirname $0`
cd ..

git checkout python_api
git pull

NAME="cortex-client"
VERSION=`git describe --long --match "release*" | awk -F"-" '{print $2}'`
RELEASE=`git describe --long --match "release*" | awk -F"-" '{print $3}'`

./scripts/build-rpm.sh

cp /var/lib/mock/epel-6-i386/result/${NAME}-${VERSION}-${RELEASE}*.noarch.rpm /var/www/html/public/comodit-trunk/centos/6.0/noarch/
cp /var/lib/mock/epel-6-i386/result/${NAME}-${VERSION}-${RELEASE}*.src.rpm /var/www/html/public/comodit-trunk/centos/6.0/SRPMS/

cp /var/lib/mock/fedora-14-i386/result/${NAME}-${VERSION}-${RELEASE}*.noarch.rpm /var/www/html/public/comodit-trunk/fedora/14/noarch/
cp /var/lib/mock/fedora-14-i386/result/${NAME}-${VERSION}-${RELEASE}*.src.rpm /var/www/html/public/comodit-trunk/fedora/14/SRPMS/

cp /var/lib/mock/fedora-15-i386/result/${NAME}-${VERSION}-${RELEASE}*.noarch.rpm /var/www/html/public/comodit-trunk/fedora/15/noarch/
cp /var/lib/mock/fedora-15-i386/result/${NAME}-${VERSION}-${RELEASE}*.src.rpm /var/www/html/public/comodit-trunk/fedora/15/SRPMS/

cp -n /var/www/html/public/comodit-trunk/centos/6.0/noarch/*.rpm /var/www/html/public/comodit-trunk/centos/6.0/i686/
cp -n /var/www/html/public/comodit-trunk/centos/6.0/noarch/*.rpm /var/www/html/public/comodit-trunk/centos/6.0/x86_64/

cp -n /var/www/html/public/comodit-trunk/fedora/14/noarch/*.rpm /var/www/html/public/comodit-trunk/fedora/14/i686/
cp -n /var/www/html/public/comodit-trunk/fedora/14/noarch/*.rpm /var/www/html/public/comodit-trunk/fedora/14/x86_64/

cp -n /var/www/html/public/comodit-trunk/fedora/15/noarch/*.rpm /var/www/html/public/comodit-trunk/fedora/15/i686/
cp -n /var/www/html/public/comodit-trunk/fedora/15/noarch/*.rpm /var/www/html/public/comodit-trunk/fedora/15/x86_64/
