#!/bin/bash

# Exit on errors
set -e
source config

NAME="comodit-client"

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

sed "s/#VERSION#/${VERSION}/g" rpmbuild/SPECS/${NAME}.spec.template > rpmbuild/SPECS/${NAME}.spec
sed -i "s/#RELEASE#/${RELEASE}/g" rpmbuild/SPECS/${NAME}.spec
sed -i "s/#COMMIT#/${COMMIT}/g" rpmbuild/SPECS/${NAME}.spec

# Generate version file
echo "VERSION=\""$VERSION"\"" > comodit_client/version.py
echo "RELEASE=\""$RELEASE"\"" >> comodit_client/version.py

mkdir -p rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Do not tar directly in SOURCES directory to escape error
# Do not tar directly in SOURCES directory to escape error
tar -cvzf ${NAME}-${VERSION}-${RELEASE}.tar.gz \
--exclude .git \
--exclude .gitignore \
--exclude debian \
--exclude scripts \
--exclude test \
--exclude rpmbuild/BUILD \
--exclude rpmbuild/BUILDROOT \
--exclude rpmbuild/SOURCES \
--exclude gitmodules  *

mv ${NAME}-${VERSION}-${RELEASE}.tar.gz rpmbuild/SOURCES

rpmbuild --define "_topdir $(pwd)/rpmbuild" -ba rpmbuild/SPECS/${NAME}.spec

if [ -f "/usr/bin/mock" ]
then
  for platform in "${PLATFORMS[@]}"
  do
    /usr/bin/mock --bootstrap-chroot -r ${platform} --rebuild rpmbuild/SRPMS/${NAME}-${VERSION}-${RELEASE}*.src.rpm
    mkdir -p ${HOME}/packages-dev/${platform}
    mv /var/lib/mock/${platform}/result/*.rpm ${HOME}/packages-dev/${platform}
  done
fi
