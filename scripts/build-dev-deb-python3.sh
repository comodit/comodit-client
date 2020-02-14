#!/bin/bash

NAME="comodit-client"
TMP_DIR=/tmp/comodit-client

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

mkdir -p ../builder-packages/python3

# Build package
DIST_DIR=${TMP_DIR}/dist
python setup.py sdist --dist-dir=${DIST_DIR}
mv ${DIST_DIR}/$NAME-$VERSION-$RELEASE.tar.gz $NAME\_$VERSION.$RELEASE.orig.tar.gz

cp debian/python3-rules.template debian/rules
cp debian/python3-control.template debian/control

dpkg-buildpackage -i -I -d -rfakeroot

mv ../*.deb ../builder-packages/python3
mv ../*.dsc ../builder-packages/python3
mv ../*.tar.gz ../builder-packages/python3

# Clean-up
python setup.py clean
make -f debian/rules clean
find . -name '*.pyc' -delete

rm -rf *.egg-info
rm -rf ../*.changes
rm -rf ../*.buildinfo
rm -rf ../*.tar.gz
