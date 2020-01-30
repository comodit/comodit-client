#!/bin/bash

# Exit on errors
set -e
source config

NAME="comodit-client"
ENV="python"

git branch

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

COMMIT=`git describe --tags --long --match "release-$VERSION" | awk -F"-" '{print $4}'`

sed "s/#NAME#/${ENV}-${NAME}/g" rpmbuild/SPECS/${ENV}-${NAME}.spec.template > rpmbuild/SPECS/${ENV}-${NAME}.spec
sed -i "s/#VERSION#/${VERSION}/g" rpmbuild/SPECS/${ENV}-${NAME}.spec
sed -i "s/#RELEASE#/${RELEASE}/g" rpmbuild/SPECS/${ENV}-${NAME}.spec
sed -i "s/#COMMIT#/${COMMIT}/g" rpmbuild/SPECS/${ENV}-${NAME}.spec

# Generate version file
echo "VERSION=\""$VERSION"\"" > comodit_client/version.py
echo "RELEASE=\""$RELEASE"\"" >> comodit_client/version.py

mkdir -p rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Do not tar directly in SOURCES directory to escape error
tar -cvzf ${ENV}-${NAME}-${VERSION}-${RELEASE}.tar.gz * \
--exclude .git \
--exclude debian \
--exclude scripts \
--exclude deb_dist \
--exclude test \
--exclude gitignorel \
--exclude gitmodules 

mv ${ENV}-${NAME}-${VERSION}-${RELEASE}.tar.gz rpmbuild/SOURCES

rpmbuild --define "_topdir $(pwd)/rpmbuild" -ba rpmbuild/SPECS/${ENV}-${NAME}.spec

if [ -f "/usr/bin/mock" ]
then
  for platform in "${PLATFORMS[@]}"
  do
    /usr/bin/mock -r ${platform} --rebuild rpmbuild/SRPMS/${ENV}-${NAME}-${VERSION}-${RELEASE}*.src.rpm
    mkdir -p ${HOME}/packages/${platform}
    mv /var/lib/mock/${platform}/result/*.rpm ${HOME}/packages/${platform}
  done

  for platform in "${SYSTEMD_PLATFORMS[@]}"
  do
    /usr/bin/mock --bootstrap-chroot -r ${platform} --define "use_systemd 1" --rebuild rpmbuild/SRPMS/${ENV}-${NAME}-${VERSION}-${RELEASE}*.src.rpm
    mkdir -p ${HOME}/packages/${platform}
    mv /var/lib/mock/${platform}/result/*.rpm ${HOME}/packages/${platform}
  done
fi
