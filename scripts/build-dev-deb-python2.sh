#!/bin/bash
source config

NAME="comodit-client"
TMP_DIR=/tmp/comodit-client
PACKAGES=packages-dev

cp debian/.pbuilderrc /home/$USERNAME/ -f

cd `dirname $0`
cd ..

# Set version information
if [ -z $1 ]
then
  # Get the latest release*dev tag  
  VERSION=`git describe --long --match "release*dev" | awk -F"-" '{print $2}'`
else
  VERSION=$1
fi

if [ -z $2 ]
then
  # How much commit since last release*dev tag ?
  RELEASE=`git describe --long --match "release*dev" | awk -F"-" '{print $3}'`
else
  RELEASE=$2
fi

COMMIT=`git describe --long --match "release*dev" | awk -F"-" '{print $4}'`
MESSAGE="Release $VERSION-$RELEASE-$COMMIT"

# Generate version file
echo "VERSION=\""$VERSION"\"" > comodit_client/version.py
echo "RELEASE=\""$RELEASE"\"" >> comodit_client/version.py

debchange --newversion $VERSION-$RELEASE "$MESSAGE"

mkdir -p ../builder-packages/python2

# Build package
DIST_DIR=${TMP_DIR}/dist
python2 setup.py sdist --dist-dir=${DIST_DIR}
mv ${DIST_DIR}/$NAME-$VERSION-$RELEASE.tar.gz $NAME\_$VERSION.$RELEASE.orig.tar.gz

cp debian/python2-rules.template debian/rules
cp debian/python2-control.template debian/control

dpkg-buildpackage -i -I -d -rfakeroot

mv ../*.deb ../builder-packages/python2
mv ../*.dsc ../builder-packages/python2
mv ../*.tar.gz ../builder-packages/python2

# Clean-up
python2 setup.py clean
make -f debian/rules clean
find . -name '*.pyc' -delete

rm -rf *.egg-info
rm -rf ../*.changes
rm -rf ../*.buildinfo
rm -rf ../*.tar.gz

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
  sudo HOME=/home/$USERNAME DIST=$tab ARCH=amd64 /usr/sbin/cowbuilder --build ../builder-packages/python2/comodit-client*.dsc

  mkdir -p /home/$USERNAME/$PACKAGES/$tab-amd64

  sudo mv -f /var/cache/pbuilder/$tab-amd64/result/*deb /home/$USERNAME/$PACKAGES/$tab-amd64
done

sudo find /var/cache/pbuilder -name *.changes -exec rm -fr {} \;
sudo find /var/cache/pbuilder -name *.dsc -exec rm -fr {} \;

