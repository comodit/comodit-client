#!/bin/bash
echo "Building cortex-client from master"

set -e

cd `dirname $0`
cd ..

git checkout master
git pull

NAME="cortex-client"
VERSION=`git describe --long --match "release*dev" | awk -F"-" '{print $2}'`
RELEASE=`git describe --long --match "release*dev" | awk -F"-" '{print $3}'`

./scripts/build-rpm.sh
deploy-trunk /var/lib/mock/epel-6-i386/result/${NAME}-${VERSION}-${RELEASE}.el6.noarch.rpm /centos
deploy-trunk /var/lib/mock/fedora-15-i386/result/${NAME}-${VERSION}-${RELEASE}.fc15.noarch.rpm /fedora/15
deploy-trunk /var/lib/mock/fedora-16-i386/result/${NAME}-${VERSION}-${RELEASE}.fc16.noarch.rpm /fedora/16
updaterepo
