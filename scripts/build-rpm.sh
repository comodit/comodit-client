#!/bin/bash

VERSION=`git describe --long --match "release*" | awk -F"-" '{print $2}'`
RELEASE=`git describe --long --match "release*" | awk -F"-" '{print $3}'`
COMMIT=`git describe --long --match "release*" | awk -F"-" '{print $4}'`

NAME=cortex-client
TAR_CONTENT="cortex_client templates conf setup.py cortex-client scripts/completions.sh"
PLATFORMS=(epel-6-i386 fedora-14-i386 fedora-15-i386)

cd `dirname $0`
cd ..

sed "s/#VERSION#/${VERSION}/g" rpmbuild/SPECS/${NAME}.spec.template > rpmbuild/SPECS/${NAME}.spec
sed -i "s/#RELEASE#/${RELEASE}/g" rpmbuild/SPECS/${NAME}.spec
sed -i "s/#COMMIT#/${COMMIT}/g" rpmbuild/SPECS/${NAME}.spec

tar -cvzf $HOME/rpmbuild/SOURCES/${NAME}-${VERSION}-${RELEASE}.tar.gz ${TAR_CONTENT}
rpmbuild -ba rpmbuild/SPECS/${NAME}.spec

for platform in "${PLATFORMS[@]}"
do
    /usr/bin/mock -r ${platform} --rebuild $HOME/rpmbuild/SRPMS/${NAME}-${VERSION}-${RELEASE}*.src.rpm
done
