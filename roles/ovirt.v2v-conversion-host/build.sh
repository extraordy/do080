#!/bin/bash

RPM_VERSION="1.9.1"
if git describe --exact-match --tags --match "v[0-9]*" > /dev/null 2>&1 ; then
    RPM_RELEASE="1"
else
    GIT="$(
        git describe --always --tags --dirty=.dr |
        sed -r 's/^/git/; s/^[^-]*-//; s/-g/.git/; s/-/_/g'
    )"
    RPM_RELEASE="0.$GIT.$(date -u +%Y%m%d%H%M%S)"
fi

ROLE_NAME="oVirt.v2v-conversion-host"
PACKAGE_NAME="ovirt-ansible-v2v-conversion-host"
PREFIX=/usr/local
DATAROOT_DIR=${DATAROOT_DIR:-${PREFIX}/share}
ROLES_DATAROOT_DIR=$DATAROOT_DIR/ansible/roles
DOC_DIR=$DATAROOT_DIR/doc
PKG_DATA_DIR=${PKG_DATA_DIR:-$ROLES_DATAROOT_DIR/$PACKAGE_NAME}
PKG_DATA_DIR_ORIG=${PKG_DATA_DIR_ORIG:-$PKG_DATA_DIR}
PKG_DOC_DIR=${PKG_DOC_DIR:-$DOC_DIR/$PACKAGE_NAME}
AUX_DATA_DIR=${AUX_DATA_DIR:-${DATAROOT_DIR}/${PACKAGE_NAME}}

DISPLAY_VERSION=$PACKAGE$RPM_VERSION

TARBALL="$PACKAGE_NAME-$RPM_VERSION.tar.gz"

dist() {
  echo "Creating tar archive '$TARBALL' ... "
  sed \
   -e "s|@RPM_VERSION@|$RPM_VERSION|g" \
   -e "s|@RPM_RELEASE@|$RPM_RELEASE|g" \
   -e "s|@PACKAGE_NAME@|$PACKAGE_NAME|g" \
   < "$PACKAGE_NAME.spec.in" > "$PACKAGE_NAME.spec"

  git ls-files | tar --files-from /proc/self/fd/0 -czf "$TARBALL" "$PACKAGE_NAME.spec"
  echo "tar archive '$TARBALL' created."
}

install() {
  echo "Installing data..."
  mkdir -p $PKG_DATA_DIR
  mkdir -p $PKG_DOC_DIR

  cp -pR defaults/ $PKG_DATA_DIR
  cp -pR files/ $PKG_DATA_DIR
  cp -pR meta/ $PKG_DATA_DIR
  cp -pR tasks/ $PKG_DATA_DIR

  mkdir -p "$AUX_DATA_DIR"
  mkdir -p "$AUX_DATA_DIR/playbooks"
  cp -pR examples/*.yml "$AUX_DATA_DIR/playbooks"

  echo "Installation done."
}

$1
