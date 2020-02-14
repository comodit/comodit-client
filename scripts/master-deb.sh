#!/bin/bash

set -e

if [[ $1 == dev ]]
then	
  scripts/build-dev-deb.sh
  scripts/build-dev-deb-python2.sh 
  scripts/build-dev-deb-python3.sh
fi
if [[ $1 == prod ]]
then
  scripts/build-deb.sh	
  scripts/build-deb-python2.sh 
  scripts/build-deb-python3.sh
fi

scripts/build-all-deb.sh $1
scripts/build-all-deb-withPython3 $1
