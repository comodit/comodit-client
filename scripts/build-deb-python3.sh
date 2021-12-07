#!/bin/bash

source config

NAME="comodit-client"
TMP_DIR=/tmp/comodit-client
PACKAGES=packages-prod

cp debian/.pbuilderrc /home/$USERNAME/ -f

cd `dirname $0`
cd ..

# Set version information
if [ -z $1 ]
then
 # Get the latest tag on the current branch
VERSION=`git describe --abbrev=0 --tags --match "*[^dev]" | awk -F"-" '{print $2}'` 
else
  VERSION=$1
fi

if [ -z $2 ]
then
  RELEASE=1
else
  RELEASE=$2
fi

COMMIT=`git describe --tags --long --match "release-${VERSION}" | awk -F"-" '{print $4}'`
MESSAGE="Release $VERSION-$RELEASE-$COMMIT"

debchange -b --newversion $VERSION-$RELEASE "$MESSAGE"

mkdir -p ../builder-packages/python3

# Generate version file
echo "VERSION=\""$VERSION"\"" > comodit_client/version.py
echo "RELEASE=\""$RELEASE"\"" >> comodit_client/version.py

# Build package
DIST_DIR=${TMP_DIR}/dist
python3 setup.py sdist --dist-dir=${DIST_DIR}
mv ${DIST_DIR}/$NAME-$VERSION-$RELEASE.tar.gz $NAME\_$VERSION.$RELEASE.orig.tar.gz

cp debian/python3-rules.template debian/rules
cp debian/python3-control.template debian/control

dpkg-buildpackage -i -I -rfakeroot

mv ../*.deb ../builder-packages/python3
mv ../*.dsc ../builder-packages/python3
mv ../*.tar.gz ../builder-packages/python3

# Clean-up
python3 setup.py clean
make -f debian/rules clean
find . -name '*.pyc' -delete

rm -rf *.egg-info
rm ../*.changes -f
rm ../*.buildinfo -f
rm ../*.tar.gz -f

for tab in "${TABS[@]}"
do
  # Create distribution directory if not exist
  sudo mkdir -p /var/cache/pbuilder/$tab-amd64/aptcache

  # If it is a Debian distribution else it is Ubuntu
  if [ $tab = 'stretch' ] || [ $tab = 'buster' ] || [ $tab = 'bullseye' ]; then
    # Create base.cow distribution 
    sudo HOME=/home/$USERNAME DIST=$tab /usr/sbin/cowbuilder --create --basepath /var/cache/pbuilder/$tab-amd64/base.cow --distribution $tab --debootstrapopts --arch --debootstrapopts amd64
  else
    sudo HOME=/home/$USERNAME DIST=$tab /usr/sbin/cowbuilder --create --basepath /var/cache/pbuilder/$tab-amd64/base.cow --distribution $tab --components "main universe" --debootstrapopts --arch --debootstrapopts amd64
  fi

  # Build packages 
  sudo HOME=/home/$USERNAME DIST=$tab ARCH=amd64 /usr/sbin/cowbuilder --build ../builder-packages/python3/comodit-client*.dsc

  mkdir -p /home/$USERNAME/$PACKAGES/$tab-amd64

  sudo mv -f /var/cache/pbuilder/$tab-amd64/result/*deb /home/$USERNAME/$PACKAGES/$tab-amd64
done

sudo find /var/cache/pbuilder -name *.changes -exec rm -fr {} \;
sudo find /var/cache/pbuilder -name *.dsc -exec rm -fr {} \;

