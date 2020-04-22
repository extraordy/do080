#!/bin/bash

VERSION="1.0.4"
MILESTONE=
RPM_RELEASE="1"

ROLE_NAME="ovirt.shutdown_env"
PACKAGE_NAME="ovirt-ansible-shutdown-env"
PREFIX=/usr/local
DATAROOT_DIR=$PREFIX/share
ROLES_DATAROOT_DIR=$DATAROOT_DIR/ansible/roles
DOC_DIR=$DATAROOT_DIR/doc
PKG_DATA_DIR=${PKG_DATA_DIR:-$ROLES_DATAROOT_DIR/$PACKAGE_NAME}
PKG_DATA_DIR_ORIG=${PKG_DATA_DIR_ORIG:-$PKG_DATA_DIR}
PKG_DOC_DIR=${PKG_DOC_DIR:-$DOC_DIR/$PACKAGE_NAME}
ROLENAME_LEGACY_NOPREFIX="${ROLENAME_LEGACY:-$ROLES_DATAROOT_DIR/ovirt-shutdown-env}"
ROLENAME_LEGACY_DASH="${ROLENAME_LEGACY:-$ROLES_DATAROOT_DIR/ovirt.shutdown-env}"
ROLENAME_LEGACY_UPPERCASE="${ROLENAME_LEGACY_UPPERCASE:-$ROLES_DATAROOT_DIR/oVirt.shutdown-env}"

RPM_VERSION=$VERSION
PACKAGE_VERSION=$VERSION
[ -n "$MILESTONE" ] && PACKAGE_VERSION+="_$MILESTONE"
DISPLAY_VERSION=$PACKAGE$VERSION

TARBALL="$PACKAGE_NAME-$PACKAGE_VERSION.tar.gz"

dist() {
  echo "Creating tar archive '$TARBALL' ... "
  sed \
   -e "s|@RPM_VERSION@|$RPM_VERSION|g" \
   -e "s|@RPM_RELEASE@|$RPM_RELEASE|g" \
   -e "s|@PACKAGE_NAME@|$PACKAGE_NAME|g" \
   -e "s|@PACKAGE_VERSION@|$PACKAGE_VERSION|g" \
   < $PACKAGE_NAME.spec.in > $PACKAGE_NAME.spec

  git ls-files | tar --files-from /proc/self/fd/0 -czf "$TARBALL" $PACKAGE_NAME.spec
  echo "tar archive '$TARBALL' created."
}

install() {
  echo "Installing data..."
  mkdir -p $PKG_DATA_DIR
  mkdir -p $PKG_DOC_DIR

  # Create symlinks for backward compatibility with legacy role names:
  ln -f -s $PKG_DATA_DIR_ORIG $ROLENAME_LEGACY_NOPREFIX
  ln -f -s $PKG_DATA_DIR_ORIG $ROLENAME_LEGACY_DASH
  ln -f -s $PKG_DATA_DIR_ORIG $ROLENAME_LEGACY_UPPERCASE

  cp -pR defaults/ $PKG_DATA_DIR
  cp -pR library/ $PKG_DATA_DIR
  cp -pR tasks/ $PKG_DATA_DIR

  echo "Installation done."
}

$1
