#!/bin/bash

NAME="comodit-client"
TMP_DIR=/tmp/comodit-client

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

mkdir -p ../builder-packages/python2

# Generate version file
echo "VERSION=\""$VERSION"\"" > comodit_client/version.py
echo "RELEASE=\""$RELEASE"\"" >> comodit_client/version.py

# Build package
DIST_DIR=${TMP_DIR}/dist
python setup.py sdist --dist-dir=${DIST_DIR}
mv ${DIST_DIR}/$NAME-$VERSION-$RELEASE.tar.gz $NAME\_$VERSION.$RELEASE.orig.tar.gz

cp debian/python2-rules.template debian/rules
cp debian/python2-control.template debian/control

dpkg-buildpackage -i -I -rfakeroot

mv ../*.deb ../builder-packages/python2
mv ../*.dsc ../builder-packages/python2
mv ../*.tar.gz ../builder-packages/python2

# Clean-up
python setup.py clean
make -f debian/rules clean
find . -name '*.pyc' -delete

rm -rf *.egg-info
rm ../*.changes -f
rm ../*.buildinfo -f
rm ../*.tar.gz -f
