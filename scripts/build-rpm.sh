#!/bin/bash

NAME="comodit-client"
SPEC_FILE_NAME="comodit-client"
PLATFORMS="epel-6-i386 fedora-16-i386 fedora-17-i386"
TAR_CONTENT="cortex_client templates setup.py comodit auto_completion/comodit doc/comodit.1 README rpmbuild/etc"

cd `dirname $0`
cd ..

# Set version information
. scripts/build-pkg-functions
set_version $1 $2
generate_version_file $VERSION $RELEASE

tar -cvzf $HOME/rpmbuild/SOURCES/${NAME}-${VERSION}-${RELEASE}.tar.gz ${TAR_CONTENT}

sed "s/#VERSION#/${VERSION}/g" rpmbuild/SPECS/${SPEC_FILE_NAME}.spec.template > rpmbuild/SPECS/${SPEC_FILE_NAME}.spec
sed -i "s/#RELEASE#/${RELEASE}/g" rpmbuild/SPECS/${SPEC_FILE_NAME}.spec
sed -i "s/#COMMIT#/${COMMIT}/g" rpmbuild/SPECS/${SPEC_FILE_NAME}.spec
rpmbuild -ba rpmbuild/SPECS/${SPEC_FILE_NAME}.spec

for platform in $PLATFORMS
do
    /usr/bin/mock -r ${platform} --rebuild $HOME/rpmbuild/SRPMS/${NAME}-${VERSION}-${RELEASE}*.src.rpm
done

