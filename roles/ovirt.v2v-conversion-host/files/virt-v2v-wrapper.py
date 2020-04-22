#!/usr/bin/python2
#
# vim: foldmethod=marker foldlevel=99
#
# Copyright (c) 2018 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from contextlib import contextmanager
import copy
import json
import logging
import os
import pycurl
import re
import signal
import subprocess
import sys
import tempfile
import time
import uuid

import six

if six.PY2:
    from urlparse import urlparse
    DEVNULL = open(os.devnull, 'r+')
else:
    from urllib.parse import urlparse
    xrange = range
    DEVNULL = subprocess.DEVNULL

# Wrapper version
VERSION = "12"

LOG_LEVEL = logging.DEBUG
STATE_DIR = '/tmp'
TIMEOUT = 300
VDSM_MIN_RHV = '4.2.4'  # This has to match VDSM_MIN_VERSION!
VDSM_MIN_VERSION = '4.20.31'  # RC4, final
VIRT_V2V = '/usr/bin/virt-v2v'

#
# Tweaks
#
# We cannot use the libvirt backend in virt-v2v and have to use direct backend
# for several reasons:
# - it is necessary on oVirt host when running as root; and we need to run as
#   root when using export domain as target (we use vdsm user for other
#   targets)
# - SSH transport method cannot be used with libvirt because it does not pass
#   SSH_AUTH_SOCK env. variable to the QEMU process
# - OpenStack mode has to run as root so we need direct backend there too
DIRECT_BACKEND = True


############################################################################
#
#  Host base interface {{{
#

class BaseHost(object):
    TYPE_UNKNOWN = 'unknown'
    TYPE_OSP = 'osp'
    TYPE_VDSM = 'vdsm'
    TYPE = TYPE_UNKNOWN

    # NOTE: This in reality binds output method (rhv-upload, openstack) to the
    #       host type (VDSM, EL) we run on. This is not ideal as we should be
    #       able to use any (or at least some) combinations (e.g. rhv-upload
    #       from EL system). But nobody asked for this feature yet.
    @staticmethod
    def detect(data):
        if 'export_domain' in data or \
                'rhv_url' in data:
            return BaseHost.TYPE_VDSM
        elif 'osp_environment' in data:
            return BaseHost.TYPE_OSP
        else:
            return BaseHost.TYPE_UNKNOWN

    @staticmethod
    def factory(host_type):
        if host_type == BaseHost.TYPE_OSP:
            return OSPHost()
        if host_type == BaseHost.TYPE_VDSM:
            return VDSMHost()
        else:
            raise ValueError("Cannot build host of type: %r" % host_type)

    # Interface

    def getLogs(self):
        return ('/tmp', '/tmp')

    def handle_cleanup(self, data, state):
        """ Handle cleanup after failed conversion """
        pass

    def handle_finish(self, data, state):
        """ Handle finish after successfull conversion """
        return True

    def check_install_drivers(self, data):
        error('cannot check_install_drivers for unknown host type')

    def prepare_command(self, data, v2v_args, v2v_env, v2v_caps):
        """ Prepare virt-v2v command parts that are method dependent """
        return v2v_args, v2v_env

    def set_user(self, data):
        """ Possibly switch to different user """
        pass

    def validate_data(self, data):
        """ Validate input data, fill in defaults, etc """
        error("Cannot validate data for uknown host type")
#
#  }}}
#
############################################################################
#
#  Openstack {{{
#


class OSPHost(BaseHost):
    TYPE = BaseHost.TYPE_VDSM

    def getLogs(self):
        log_dir = '/var/log/virt-v2v'
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
        return (log_dir, log_dir)

    def handle_cleanup(self, data, state):
        """ Handle cleanup after failed conversion """
        volumes = state['internal']['disk_ids'].values()
        ports = state['internal']['ports']
        # Cancel transfers
        transfers = self._run_openstack([
            'volume', 'transfer', 'request', 'list',
            '--format', 'json',
            ], data)
        if transfers is None:
            logging.error('Failed to remove transfer(s)')
        else:
            transfers = json.loads(transfers)
            # Strangely, the keys are not lowercase
            transfers = [t['ID'] for t in transfers if t['Volume'] in volumes]
            if len(transfers) > 0:
                trans_cmd = ['volume', 'transfer', 'request', 'delete']
                trans_cmd.extend(transfers)
                if self._run_openstack(trans_cmd, data) is None:
                    logging.error('Failed to remove transfer(s)')
        # Remove created ports
        if len(ports) > 0:
            logging.info('Removing ports: %r', ports)
            port_cmd = ['port', 'delete']
            port_cmd.extend(ports)
            if self._run_openstack(port_cmd, data, destination=True) is None:
                logging.error('Failed to remove port(s)')
        # Remove volumes
        if len(volumes) > 0:
            # We don't know in which project the volumes are and figuring that
            # out using openstack command can be impractical in large
            # environments. Let's just try to remove them from both.
            logging.info('Removing volume(s): %r', volumes)
            vol_cmd = ['volume', 'delete']
            vol_cmd.extend(volumes)
            if self._run_openstack(vol_cmd, data) is None:
                logging.error(
                    'Failed to remove volumes(s) from current project')
            if self._run_openstack(vol_cmd, data, destination=True) is None:
                logging.error(
                    'Failed to remove volumes(s) from destination project')

    def handle_finish(self, data, state):
        """
        Handle finish after successfull conversion

        For OpenStack this entails creating a VM instance.
        """
        # Init keystone
        if self._run_openstack(['token', 'issue'], data) is None:
            logging.error('Create VM failed')
            return False
        volumes = []
        # Build volume list
        for k in sorted(state['internal']['disk_ids'].keys()):
            volumes.append(state['internal']['disk_ids'][k])
        if len(volumes) == 0:
            logging.error('No volumes found!')
            return False
        if len(volumes) != len(state['internal']['disk_ids']):
            logging.error('Detected duplicate indices of Cinder volumes')
            logging.debug('Source volume map: %r',
                          state['internal']['disk_ids'])
            logging.debug('Assumed volume list: %r', volumes)
            return False
        # Move volumes to destination project
        for vol in volumes:
            logging.info('Transfering volume: %s', vol)
            transfer = self._run_openstack([
                'volume', 'transfer', 'request', 'create',
                '--format', 'json',
                vol,
                ], data)
            if transfer is None:
                logging.error('Failed to transfer volume')
                return False
            transfer = json.loads(transfer)
            self._run_openstack([
                'volume', 'transfer', 'request', 'accept',
                '--auth-key', transfer['auth_key'],
                transfer['id']
                ], data, destination=True)
        # Create ports
        ports = []
        for nic in data['network_mappings']:
            port_cmd = [
                'port', 'create',
                '--format', 'json',
                '--network', nic['destination'],
                '--mac-address', nic['mac_address'],
                '--enable',
                '%s_port_%s' % (data['vm_name'], len(ports)),
                ]
            if 'ip_address' in nic:
                port_cmd.extend([
                    '--fixed-ip', 'ip-address=%s' % nic['ip_address'],
                    ])
            for grp in data['osp_security_groups_ids']:
                port_cmd.extend(['--security-group', grp])
            port = self._run_openstack(port_cmd, data, destination=True)
            if port is None:
                logging.error('Failed to create port')
                return False
            port = json.loads(port)
            logging.info('Created port id=%s', port['id'])
            ports.append(port['id'])
        state['internal']['ports'] = ports
        # Create instance
        os_command = [
            'server', 'create',
            '--flavor', data['osp_flavor_id'],
            ]
        for grp in data['osp_security_groups_ids']:
            os_command.extend(['--security-group', grp])
        os_command.extend(['--volume', volumes[0]])
        for i in xrange(1, len(volumes)):
            os_command.extend([
                '--block-device-mapping',
                '%s=%s' % (self._get_disk_name(i+1), volumes[i]),
                ])
        for port in ports:
            os_command.extend(['--nic', 'port-id=%s' % port])
        os_command.append(data['vm_name'])
        # Let's get rolling...
        if self._run_openstack(os_command, data, destination=True) is None:
            logging.error('Create VM failed')
            return False
        else:
            return True

    def check_install_drivers(self, data):
        # Nothing to do for OSP
        pass

    def prepare_command(self, data, v2v_args, v2v_env, v2v_caps):
        """ Prepare virt-v2v command parts that are method dependent """
        v2v_args.extend([
            '-o', 'openstack',
            '-oo', 'server-id=%s' % data['osp_server_id'],
            '-oo', 'guest-id=%s' % data['osp_guest_id'],
            ])
        # Convert to arguments of the form os-something
        for k, v in six.iteritems(data['osp_environment']):
            v2v_args.extend([
                '-oo',
                '%s=%s' % (k.lower().replace('_', '-'), v)])
        if 'osp_volume_type_id' in data:
            v2v_args.extend([
                '-os', data['osp_volume_type_id'],
                ])
        if data['insecure_connection']:
            v2v_args.extend([
                '-oo', 'verify-server-certificate=false'
                ])
        return v2v_args, v2v_env

    def set_user(self, data):
        """ Possibly switch to different user """
        # Check we are running as root
        uid = os.geteuid()
        if uid != 0:
            sys.stderr.write('Need to run as root!\n')
            sys.exit(1)

    def validate_data(self, data):
        """ Validate input data, fill in defaults, etc """
        # Enforce direct backend
        data['backend'] = 'direct'
        # Check necessary keys
        for k in [
                'osp_destination_project_id',
                'osp_environment',
                'osp_flavor_id',
                'osp_security_groups_ids',
                'osp_server_id',
                ]:
            if k not in data:
                error('Missing argument: %s' % k)
        if 'insecure_connection' not in data:
            data['insecure_connection'] = False
        if data.get('insecure_connection', False):
            logging.info(
                'SSL verification is disabled for OpenStack connections')
        osp_arg_re = re.compile('os[-_]', re.IGNORECASE)
        for k in data['osp_environment'].keys():
            if not osp_arg_re.match(k[:3]):
                error('found invalid key in OSP environment: %s' % k)
        if 'osp_guest_id' not in data:
            data['osp_guest_id'] = uuid.uuid4()
        if not isinstance(data['osp_security_groups_ids'], list):
            error('osp_security_groups_ids must be a list')
        for mapping in data['network_mappings']:
            if 'mac_address' not in mapping:
                error('Missing mac address in one of network mappings')
        return data

    def _get_disk_name(self, index):
        if index < 1:
            raise ValueError('Index less then 1', index)
        if index > 702:
            raise ValueError('Index too large', index)
        index = index - 1
        one = index // 26
        two = index % 26
        enumid = (lambda i: chr(ord('a') + i))
        return 'vd%s%s' % ('' if one == 0 else enumid(one-1), enumid(two))

    def _run_openstack(self, cmd, data, destination=False):
        """
        Run the openstack commands with necessary arguments. When @destination
        is True the command is run in destination project. Otherwise it is run
        in current project.
        """
        command = ['openstack']
        if data.get('insecure_connection', False):
            command.append('--insecure')
        # Convert to arguments of the form os-something
        for k, v in six.iteritems(data['osp_environment']):
            command.append('--%s=%s' % (k.lower().replace('_', '-'), v))
        if destination:
            # It doesn't matter if there already is --os-project-name or
            # --os-project-id. The last argument takes precedence.
            command.append('--os-project-id=%s' %
                           data['osp_destination_project_id'])
        command.extend(cmd)
        log_command_safe(command, {})
        try:
            return subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            # NOTE: Do NOT use logging.exception() here as it leaks passwords
            # into the log!
            logging.error(
                'Command exitet with non-zero return code %d, output:\n%s\n',
                e.returncode, e.output)
            return None


#
#  }}}
#
############################################################################
#
#  RHV {{{
#


class VDSMHost(BaseHost):
    """ Encapsulates data and methods specific to oVirt/RHV environment """
    TYPE = BaseHost.TYPE_VDSM

    TOOLS_PATTERNS = [
        (7, br'RHV-toolsSetup_([0-9._]+)\.iso'),
        (6, br'rhv-tools-setup\.iso'),
        (5, br'RHEV-toolsSetup_([0-9._]+)\.iso'),
        (4, br'rhev-tools-setup\.iso'),
        (3, br'oVirt-toolsSetup_([a-z0-9._-]+)\.iso'),
        (2, br'ovirt-tools-setup\.iso'),
        (1, br'virtio-win-([0-9.]+).iso'),
        (0, br'virtio-win\.iso'),
        ]
    VDSM_LOG_DIR = '/var/log/vdsm/import'
    VDSM_MOUNTS = '/rhev/data-center/mnt'
    VDSM_CA = '/etc/pki/vdsm/certs/cacert.pem'
    VDSM_UID = 36

    def __init__(self):
        import ovirtsdk4 as sdk
        self.sdk = sdk
        # For now there are limited possibilities in how we can select
        # allocation type and format. The best thing we can do now is to base
        # the allocation on type of target storage domain.
        self.PREALLOCATED_STORAGE_TYPES = (
            self.sdk.types.StorageType.CINDER,
            self.sdk.types.StorageType.FCP,
            self.sdk.types.StorageType.GLUSTERFS,
            self.sdk.types.StorageType.ISCSI,
            self.sdk.types.StorageType.POSIXFS,
            )

    @contextmanager
    def sdk_connection(self, data):
        connection = None
        url = urlparse(data['rhv_url'])
        username = url.username if url.username is not None \
            else 'admin@internal'
        try:
            insecure = data['insecure_connection']
            connection = self.sdk.Connection(
                url=str(data['rhv_url']),
                username=str(username),
                password=str(data['rhv_password']),
                ca_file=str(data['rhv_cafile']),
                log=logging.getLogger(),
                insecure=insecure,
            )
            yield connection
        finally:
            if connection is not None:
                connection.close()

    def getLogs(self):
        """ Returns tuple with directory for virt-v2v log and wrapper log """
        return (self.VDSM_LOG_DIR, self.VDSM_LOG_DIR)

    def handle_cleanup(self, data, state):
        with self.sdk_connection(data) as conn:
            disks_service = conn.system_service().disks_service()
            transfers_service = conn.system_service().image_transfers_service()
            disk_ids = state['internal']['disk_ids'].values()
            # First stop all active transfers...
            try:
                transfers = transfers_service.list()
                transfers = [t for t in transfers if t.image.id in disk_ids]
                if len(transfers) == 0:
                    logging.debug('No active transfers to cancel')
                for transfer in transfers:
                    logging.info('Canceling transfer id=%s for disk=%s',
                                 transfer.id, transfer.image.id)
                    transfer_service = \
                        transfers_service.image_transfer_service(
                            transfer.id)
                    transfer_service.cancel()
                    # The incomplete disk will be removed automatically
                    disk_ids.remove(transfer.image.id)
            except self.sdk.Error:
                logging.exception('Failed to cancel transfers')

            # ... then delete the uploaded disks
            logging.info('Removing disks: %r', disk_ids)
            endt = time.time() + TIMEOUT
            while len(disk_ids) > 0:
                for disk_id in disk_ids:
                    try:
                        disk_service = disks_service.disk_service(disk_id)
                        disk = disk_service.get()
                        if disk.status != self.sdk.types.DiskStatus.OK:
                            continue
                        logging.info('Removing disk id=%s', disk_id)
                        disk_service.remove()
                        disk_ids.remove(disk_id)
                    except self.sdk.Error:
                        logging.exception('Failed to remove disk id=%s',
                                          disk_id)
                if time.time() > endt:
                    logging.error('Timed out waiting for disks: %r', disk_ids)
                    break
                time.sleep(1)

    def check_install_drivers(self, data):
        """ Validate and/or find ISO with guest tools and drivers """
        if 'virtio_win' in data and os.path.isabs(data['virtio_win']):
            full_path = data['virtio_win']
        else:
            iso_domain = self._find_iso_domain()

            iso_name = data.get('virtio_win')
            if iso_name is not None:
                if iso_domain is None:
                    error('ISO domain not found')
            else:
                if iso_domain is None:
                    # This is not an error
                    logging.warning('ISO domain not found' +
                                    ' (but install_drivers is true).')
                    data['install_drivers'] = False
                    return

                best_name = self._filter_iso_names(
                        iso_domain, os.listdir(iso_domain))
                if best_name is None:
                    # Nothing found, this is not an error
                    logging.warn('Could not find any ISO with drivers' +
                                 ' (but install_drivers is true).')
                    data['install_drivers'] = False
                    return
                iso_name = best_name

            full_path = os.path.join(iso_domain, iso_name)

        if not os.path.isfile(full_path):
            error("'virtio_win' must be a path or file name of image in "
                  "ISO domain")
        data['virtio_win'] = full_path
        logging.info("virtio_win (re)defined as: %s", data['virtio_win'])

    def prepare_command(self, data, v2v_args, v2v_env, v2v_caps):
        v2v_args.extend([
            '-of', data['output_format'],
            ])
        if 'allocation' in data:
            v2v_args.extend([
                '-oa', data['allocation']
                ])

        if 'rhv_url' in data:
            v2v_args.extend([
                '-o', 'rhv-upload',
                '-oc', data['rhv_url'],
                '-os', data['rhv_storage'],
                '-op', data['rhv_password_file'],
                '-oo', 'rhv-cafile=%s' % data['rhv_cafile'],
                '-oo', 'rhv-cluster=%s' % data['rhv_cluster'],
                '-oo', 'rhv-direct',
                ])
            if data['insecure_connection']:
                v2v_args.extend(['-oo', 'rhv-verifypeer=%s' %
                                ('false' if data['insecure_connection'] else
                                 'true')])

        elif 'export_domain' in data:
            v2v_args.extend([
                '-o', 'rhv',
                '-os', data['export_domain'],
                ])

        return v2v_args, v2v_env

    def set_user(self, data):
        """ Possibly switch to VDSM user """

        if 'export_domain' in data:
            # Need to be root to mount NFS share
            return

        uid = os.geteuid()
        if uid == VDSMHost.VDSM_UID:
            # logging.debug('Already running as vdsm user')
            return
        elif uid == 0:
            # We need to drop privileges and become vdsm user, but we also need
            # the proper environment for the user which is tricky to get. The
            # best thing we can do is spawn another instance. Unfortunately we
            # have already read the data from stdin. logging.debug('Starting
            # instance as vdsm user')
            cmd = '/usr/bin/sudo'
            args = [cmd, '-u', 'vdsm']
            args.extend(sys.argv)
            wrapper = subprocess.Popen(args,
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            out, err = wrapper.communicate(json.dumps(data))
            # logging.debug('vdsm instance finished')
            sys.stdout.write(out)
            sys.stderr.write(err)
            # logging.debug('Terminating root instance')
            sys.exit(wrapper.returncode)
        sys.stderr.write('Need to run as vdsm user or root!\n')
        sys.exit(1)

    def validate_data(self, data):
        """ Validate input data, fill in defaults, etc """
        # Determine whether direct backend is required
        direct_backend = DIRECT_BACKEND
        if 'export_domain' in data:
            # Cannot use libvirt backend as root on VDSM host due to
            # permissions
            direct_backend = True
        if direct_backend:
            data['backend'] = 'direct'

        # Output file format (raw or qcow2)
        if 'output_format' in data:
            if data['output_format'] not in ('raw', 'qcow2'):
                error('Invalid output format %r, expected raw or qcow2' %
                      data['output_format'])
        else:
            data['output_format'] = 'raw'

        # Targets (only export domain for now)
        if 'rhv_url' in data:
            for k in [
                    'rhv_cluster',
                    'rhv_password',
                    'rhv_storage',
                    ]:
                if k not in data:
                    error('Missing argument: %s' % k)
            if 'rhv_cafile' not in data:
                logging.info('Path to CA certificate not specified')
                data['rhv_cafile'] = VDSMHost.VDSM_CA
                logging.info('... trying VDSM default: %s',
                             data['rhv_cafile'])
        elif 'export_domain' in data:
            pass
        else:
            error('No target specified')

        # Insecure connection
        if 'insecure_connection' not in data:
            data['insecure_connection'] = False
        if data['insecure_connection']:
            logging.info(
                'SSL verification is disabled for oVirt SDK connections')

        if 'allocation' not in data:
            # Check storage domain type and decide on suitable allocation type
            # Note: This is only temporary. We should get the info from the
            # caller in the future.
            domain_type = None
            with self.sdk_connection(data) as c:
                service = c.system_service().storage_domains_service()
                domains = service.list(search='name="%s"' %
                                       str(data['rhv_storage']))
                if len(domains) != 1:
                    error('Found %d domains matching "%s"!' %
                          (len(domains), data['rhv_storage']))
                domain_type = domains[0].storage.type
            logging.info('Storage domain "%s" is of type %r',
                         data['rhv_storage'], domain_type)
            data['allocation'] = 'sparse'
            if domain_type in self.PREALLOCATED_STORAGE_TYPES:
                data['allocation'] = 'preallocated'
            logging.info('... selected allocation type is %s',
                         data['allocation'])

        return data

    def _filter_iso_names(self, iso_domain, isos):
        """ @isos is a list of file names or an iterator """
        # (priority, pattern)
        patterns = [(p[0], re.compile(p[1], re.IGNORECASE))
                    for p in self.TOOLS_PATTERNS]
        best_name = None
        best_version = None
        best_priority = -1

        for fname in isos:
            if not os.path.isfile(os.path.join(iso_domain, fname)):
                continue
            for priority, pat in patterns:
                m = pat.match(fname)
                if not m:
                    continue
                if len(m.groups()) == 0:
                    version = b''
                else:
                    version = m.group(1)
                logging.debug('Matched ISO %r (priority %d)', fname, priority)
                if best_version is None or \
                        best_priority < priority or \
                        (best_version < version and best_priority == priority):
                    best_name = fname
                    best_version = version
                    best_priority = priority

        return best_name

    def _find_iso_domain(self):
        """
        Find path to the ISO domain from available domains mounted on host
        """
        if not os.path.isdir(self.VDSM_MOUNTS):
            logging.error('Cannot find RHV domains')
            return None
        for sub in os.walk(self.VDSM_MOUNTS):

            if 'dom_md' in sub[1]:
                # This looks like a domain so focus on metadata only
                try:
                    del sub[1][sub[1].index('master')]
                except ValueError:
                    pass
                try:
                    del sub[1][sub[1].index('images')]
                except ValueError:
                    pass
                continue

            if 'blockSD' in sub[1]:
                # Skip block storage domains, we don't support ISOs there
                del sub[1][sub[1].index('blockSD')]

            if 'metadata' in sub[2] and \
                    os.path.basename(sub[0]) == 'dom_md' and \
                    self._is_iso_domain(os.path.join(sub[0], 'metadata')):
                return os.path.join(
                    os.path.dirname(sub[0]),
                    'images',
                    '11111111-1111-1111-1111-111111111111')
        return None

    def _is_iso_domain(self, path):
        """
        Check if domain is ISO domain. @path is path to domain metadata file
        """
        try:
            logging.debug('_is_iso_domain check for %s', path)
            with open(path, 'r') as f:
                for line in f:
                    if line.rstrip() == 'CLASS=Iso':
                        return True
        except OSError:
            logging.exception('Failed to read domain metadata')
        except IOError:
            logging.exception('Failed to read domain metadata')
        return False

#
#  }}}
#
############################################################################
#
#  Routines {{{
#


def error(msg):
    """
    Function to produce an error and terminate the wrapper.

    WARNING: This can be used only at the early initialization stage! Do NOT
    use this once the password files are written or there are any other
    temporary data that should be removed at exit. This function uses
    sys.exit() which overcomes the code responsible for removing the files.
    """
    logging.error(msg)
    sys.stderr.write(msg)
    sys.exit(1)


def daemonize():
    """Properly deamonizes the process and closes file desriptors."""
    sys.stderr.flush()
    sys.stdout.flush()

    pid = os.fork()
    if pid != 0:
        # Nothing more to do for the parent
        sys.exit(0)

    os.setsid()
    pid = os.fork()
    if pid != 0:
        # Nothing more to do for the parent
        sys.exit(0)

    os.umask(0)
    os.chdir('/')

    dev_null = open('/dev/null', 'w')
    os.dup2(dev_null.fileno(), sys.stdin.fileno())
    os.dup2(dev_null.fileno(), sys.stdout.fileno())
    os.dup2(dev_null.fileno(), sys.stderr.fileno())

    # Re-initialize cURL. This is necessary to re-initialze the PKCS #11
    # security tokens in NSS. Otherwise any use of SDK after the fork() would
    # lead to the error:
    #
    #    A PKCS #11 module returned CKR_DEVICE_ERROR, indicating that a
    #    problem has occurred with the token or slot.
    #
    pycurl.global_cleanup()
    pycurl.global_init(pycurl.GLOBAL_ALL)


class OutputParser(object):

    COPY_DISK_RE = re.compile(br'.*Copying disk (\d+)/(\d+) to.*')
    DISK_PROGRESS_RE = re.compile(br'\s+\((\d+\.\d+)/100%\)')
    NBDKIT_DISK_PATH_RE = re.compile(
        br'nbdkit: debug: Opening file (.*) \(.*\)')
    OVERLAY_SOURCE_RE = re.compile(
        br' *overlay source qemu URI: json:.*"file\.path": ?"([^"]+)"')
    OVERLAY_SOURCE2_RE = re.compile(
        br'libguestfs: parse_json: qemu-img info JSON output:.*'
        br'"backing-filename".*\\"file\.path\\": ?\\"([^"]+)\\"')
    VMDK_PATH_RE = re.compile(
        br'/vmfs/volumes/(?P<store>[^/]*)/(?P<vm>[^/]*)/'
        br'(?P<disk>.*?)(-flat)?\.vmdk$')
    RHV_DISK_UUID = re.compile(br'disk\.id = \'(?P<uuid>[a-fA-F0-9-]*)\'')
    OSP_VOLUME_PROPS = re.compile(
        br'openstack .*\'?volume\'? \'?set.*'
        br'\'?--property\'?'
        br' \'?virt_v2v_disk_index=(?P<volume>[0-9]+)/[0-9]+.*'
        br' \'?(?P<uuid>[a-fA-F0-9-]*)\'?$')

    def __init__(self, v2v_log):
        self._log = open(v2v_log, 'rbU')
        self._current_disk = None
        self._current_path = None

    def parse(self, state):
        line = None
        while line != b'':
            line = self._log.readline()
            state = self.parse_line(state, line)
        return state

    def parse_line(self, state, line):
        m = self.COPY_DISK_RE.match(line)
        if m is not None:
            try:
                self._current_disk = int(m.group(1))-1
                self._current_path = None
                state['disk_count'] = int(m.group(2))
                logging.info('Copying disk %d/%d',
                             self._current_disk+1, state['disk_count'])
                if state['disk_count'] != len(state['disks']):
                    logging.warning(
                        'Number of supplied disk paths (%d) does not match'
                        ' number of disks in VM (%s)',
                        len(state['disks']),
                        state['disk_count'])
            except ValueError:
                logging.exception('Conversion error')

        # VDDK
        m = self.NBDKIT_DISK_PATH_RE.match(line)
        if m is not None:
            self._current_path = m.group(1)
            if self._current_disk is not None:
                logging.info('Copying path: %s', self._current_path)
                self._locate_disk(state)

        # SSH + RHV
        m = self.OVERLAY_SOURCE_RE.match(line)
        if m is not None:
            path = m.group(1)
            # Transform path to be raltive to storage
            self._current_path = self.VMDK_PATH_RE.sub(
                br'[\g<store>] \g<vm>/\g<disk>.vmdk', path)
            if self._current_disk is not None:
                logging.info('Copying path: %s', self._current_path)
                self._locate_disk(state)

        # SSH + OpenStack
        m = self.OVERLAY_SOURCE2_RE.match(line)
        if m is not None:
            path = m.group(1)
            # Transform path to be raltive to storage
            self._current_path = self.VMDK_PATH_RE.sub(
                br'[\g<store>] \g<vm>/\g<disk>.vmdk', path)
            if self._current_disk is not None:
                logging.info('Copying path: %s', self._current_path)
                self._locate_disk(state)

        m = self.DISK_PROGRESS_RE.match(line)
        if m is not None:
            if self._current_path is not None and \
                    self._current_disk is not None:
                try:
                    state['disks'][self._current_disk]['progress'] = \
                        float(m.group(1))
                    logging.debug('Updated progress: %s', m.group(1))
                except ValueError:
                    logging.exception('Conversion error')
            else:
                logging.debug('Skipping progress update for unknown disk')

        m = self.RHV_DISK_UUID.match(line)
        if m is not None:
            path = state['disks'][self._current_disk]['path']
            disk_id = m.group('uuid')
            state['internal']['disk_ids'][path] = disk_id
            logging.debug('Path \'%s\' has disk id=\'%s\'', path, disk_id)

        # OpenStack volume index and UUID
        m = self.OSP_VOLUME_PROPS.match(line)
        if m is not None:
            volume_id = m.group('uuid').decode('utf-8')
            index = int(m.group('volume'))
            state['internal']['disk_ids'][index] = volume_id
            logging.debug(
                'Volume at index %d has id=\'%s\'',
                index, volume_id)

        return state

    def close(self):
        self._log.close()

    def _locate_disk(self, state):
        if self._current_disk is None:
            # False alarm, not copying yet
            return

        # NOTE: We assume that _current_disk is monotonic
        for i in xrange(self._current_disk, len(state['disks'])):
            if state['disks'][i]['path'] == self._current_path:
                if i == self._current_disk:
                    # We have correct index
                    logging.debug('Found path at correct index')
                else:
                    # Move item to current index
                    logging.debug('Moving path from index %d to %d', i,
                                  self._current_disk)
                    d = state['disks'].pop(i)
                    state['disks'].insert(self._current_disk, d)
                return

        # Path not found
        logging.debug('Path \'%s\' not found in %r', self._current_path,
                      state['disks'])
        state['disks'].insert(
            self._current_disk,
            {
                'path': self._current_path,
                'progress': 0,
            })


@contextmanager
def log_parser(v2v_log):
    parser = None
    try:
        parser = OutputParser(v2v_log)
        yield parser
    finally:
        if parser is not None:
            parser.close()


def write_state(state):
    state_file = state['internal']['state_file']
    state = state.copy()
    del state['internal']
    with open(state_file, 'w') as f:
        json.dump(state, f)


def prepare_command(data, v2v_caps, agent_sock=None):
    v2v_args = [
        VIRT_V2V, '-v', '-x',
        data['vm_name'],
        '--bridge', 'ovirtmgmt',
        '--root', 'first'
    ]

    if data['transport_method'] == 'vddk':
        v2v_args.extend([
            '-i', 'libvirt',
            '-ic', data['vmware_uri'],
            '-it', 'vddk',
            '-io', 'vddk-libdir=%s' % '/opt/vmware-vix-disklib-distrib',
            '-io', 'vddk-thumbprint=%s' % data['vmware_fingerprint'],
            '--password-file', data['vmware_password_file'],
            ])
    elif data['transport_method'] == 'ssh':
        v2v_args.extend([
            '-i', 'vmx',
            '-it', 'ssh',
            ])

    if 'network_mappings' in data:
        for mapping in data['network_mappings']:
            if 'mac_address' in mapping and 'mac-option' in v2v_caps:
                v2v_args.extend(['--mac', '%s:bridge:%s' %
                                (mapping['mac_address'],
                                    mapping['destination'])])
            else:
                v2v_args.extend(['--bridge', '%s:%s' %
                                (mapping['source'], mapping['destination'])])

    # Prepare environment
    v2v_env = os.environ.copy()
    v2v_env['LANG'] = 'C'
    if 'backend' in data:
        if data['backend'] == 'direct':
            logging.debug('Using direct backend. Hack, hack...')
        v2v_env['LIBGUESTFS_BACKEND'] = data['backend']
    if 'virtio_win' in data:
        v2v_env['VIRTIO_WIN'] = data['virtio_win']
    if agent_sock is not None:
        v2v_env['SSH_AUTH_SOCK'] = agent_sock

    return (v2v_args, v2v_env)


def wrapper(host, data, state, v2v_log, v2v_caps, agent_sock=None):

    v2v_args, v2v_env = prepare_command(data, v2v_caps, agent_sock)
    v2v_args, v2v_env = host.prepare_command(
        data, v2v_args, v2v_env, v2v_caps)

    proc = None
    with open(v2v_log, 'w') as log:
        logging.info('Starting virt-v2v:')
        log_command_safe(v2v_args, v2v_env)
        proc = subprocess.Popen(
                v2v_args,
                stdin=DEVNULL,
                stderr=subprocess.STDOUT,
                stdout=log,
                env=v2v_env,
                )

    try:
        state['started'] = True
        state['pid'] = proc.pid
        write_state(state)
        with log_parser(v2v_log) as parser:
            while proc.poll() is None:
                state = parser.parse(state)
                write_state(state)
                time.sleep(5)
            logging.info('virt-v2v terminated with return code %d',
                         proc.returncode)
            state = parser.parse(state)
    except Exception:
        logging.exception('Error while monitoring virt-v2v')
        if proc.poll() is None:
            logging.info('Killing virt-v2v process')
            proc.kill()

    state['return_code'] = proc.returncode
    write_state(state)

    if proc.returncode != 0:
        state['failed'] = True
    write_state(state)


def write_password(password, password_files):
    pfile = tempfile.mkstemp(suffix='.v2v')
    password_files.append(pfile[1])
    os.write(pfile[0], bytes(password.encode('utf-8')))
    os.close(pfile[0])
    return pfile[1]


def spawn_ssh_agent(data):
    try:
        out = subprocess.check_output(['ssh-agent'])
        logging.debug('ssh-agent: %s' % out)
        sock = re.search(br'^SSH_AUTH_SOCK=([^;]+);', out, re.MULTILINE)
        pid = re.search(br'^echo Agent pid ([0-9]+);', out, re.MULTILINE)
        if not sock or not pid:
            logging.error(
                'Incomplete match of ssh-agent output; sock=%r; pid=%r',
                sock, pid)
            return None, None
        agent_sock = sock.group(1)
        agent_pid = int(pid.group(1))
        logging.info('SSH Agent started with PID %d', agent_pid)
    except subprocess.CalledProcessError:
        logging.exception('Failed to start ssh-agent')
        return None, None
    except ValueError:
        logging.exception('Failed to parse ssh-agent output')
        return None, None
    env = os.environ.copy()
    env['SSH_AUTH_SOCK'] = agent_sock
    cmd = ['ssh-add']
    if 'ssh_key_file' in data:
        logging.info('Using custom SSH key')
        cmd.append(data['ssh_key_file'])
    else:
        logging.info('Using SSH key(s) from ~/.ssh')
    try:
        out = subprocess.check_output(
            cmd,
            env=env,
            stderr=subprocess.STDOUT,
            stdin=DEVNULL)
    except subprocess.CalledProcessError as e:
        logging.exception('Failed to add SSH keys to the agent!')
        logging.error("ssh-add output: %s", e.output)
        os.kill(agent_pid, signal.SIGTERM)
        return None, None
    return agent_pid, agent_sock


def virt_v2v_capabilities():
    try:
        return subprocess.check_output(['virt-v2v', u'--machine-readable']) \
                         .split('\n')
    except subprocess.CalledProcessError:
        logging.exception('Failed to start virt-v2v')
        return None


def log_command_safe(args, env, log=None):
    args = copy.deepcopy(args)
    env = copy.deepcopy(env)
    # Filter command
    arg_re = re.compile('([^=]*password[^=]*)=(.*)', re.IGNORECASE)
    for i in xrange(1, len(args)):
        m = arg_re.match(args[i])
        if m:
            args[i] = '%s=*****' % m.group(1)
    # Filter environment
    env_re = re.compile('password', re.IGNORECASE)
    for k in env.keys():
        if env_re.search(k):
            env[k] = '*****'
    # Log the result
    if log is None:
        log = logging
    log.info('Executing command: %r, environment: %r', args, env)

#
#  }}}
#
############################################################################
#
#  Checks {{{
#


def check_rhv_guest_tools():
    """
    Make sure there is ISO domain with at least one ISO with windows drivers.
    Preferably RHV Guest Tools ISO.
    """
    host = BaseHost.factory(BaseHost.TYPE_VDSM)
    data = {'install_drivers': True}
    host.check_install_drivers(data)
    return ('virtio_win' in data)


def check_rhv_version():
    import rpmUtils.transaction
    import rpmUtils.miscutils

    ts = rpmUtils.transaction.initReadOnlyTransaction()
    match = ts.dbMatch('name', 'vdsm')
    if len(match) >= 1:
        vdsm = match.next()
        res = rpmUtils.miscutils.compareEVR(
            (vdsm['epoch'], vdsm['version'], None),  # Ignore release number
            rpmUtils.miscutils.stringToVersion(VDSM_MIN_VERSION))
        return (res >= 0)
    print('Minimal required oVirt/RHV version is %s' % VDSM_MIN_RHV)
    return False


CHECKS = {
    'rhv-guest-tools': check_rhv_guest_tools,
    'rhv-version': check_rhv_version,
}

#  }}}
#
############################################################################
#
#  Main {{{
#


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--checks':
            for check in CHECKS.keys():
                print("%s" % check)
            sys.exit(0)
        if sys.argv[1][:8] == '--check-':
            check = CHECKS.get(sys.argv[1][8:])
            if check is not None and check():
                sys.exit(0)
            else:
                sys.exit(1)
        if sys.argv[1] == '--version':
            print('virt-v2v-wrapper %s' % VERSION)
            sys.exit(0)

    # Read and parse input -- hopefully this should be safe to do as root
    data = json.load(sys.stdin)

    host_type = BaseHost.detect(data)
    host = BaseHost.factory(host_type)
    host.set_user(data)

    # The logging is delayed after we now which user runs the wrapper.
    # Otherwise we would have two logs.
    log_tag = '%s-%d' % (time.strftime('%Y%m%dT%H%M%S'), os.getpid())
    log_dirs = host.getLogs()
    v2v_log = os.path.join(log_dirs[0], 'v2v-import-%s.log' % log_tag)
    wrapper_log = os.path.join(log_dirs[1],
                               'v2v-import-%s-wrapper.log' % log_tag)
    state_file = os.path.join(STATE_DIR, 'v2v-import-%s.state' % log_tag)

    log_format = '%(asctime)s:%(levelname)s:' \
        + ' %(message)s (%(module)s:%(lineno)d)'
    logging.basicConfig(
        level=LOG_LEVEL,
        filename=wrapper_log,
        format=log_format)

    logging.info('Wrapper version %s, uid=%d', VERSION, os.getuid())

    logging.info('Will store virt-v2v log in: %s', v2v_log)
    logging.info('Will store state file in: %s', state_file)

    password_files = []

    # Collect virt-v2v capabilities
    virt_v2v_caps = virt_v2v_capabilities()
    if virt_v2v_caps is None:
        error('Could not get virt-v2v capabilities.')
    logging.debug("virt-v2v capabilities: %r" % virt_v2v_caps)

    try:

        # Make sure all the needed keys are in data. This is rather poor
        # validation, but...
        if 'vm_name' not in data:
                error('Missing vm_name')

        # Transports (only VDDK for now)
        if 'transport_method' not in data:
            error('No transport method specified')
        if data['transport_method'] not in ('ssh', 'vddk'):
            error('Unknown transport method: %s', data['transport_method'])

        if data['transport_method'] == 'vddk':
            for k in [
                    'vmware_fingerprint',
                    'vmware_uri',
                    'vmware_password',
                    ]:
                if k not in data:
                    error('Missing argument: %s' % k)

        # Network mappings
        if 'network_mappings' in data:
            if isinstance(data['network_mappings'], list):
                for mapping in data['network_mappings']:
                    if not all(
                            k in mapping for k in ("source", "destination")):
                        error("Both 'source' and 'destination'"
                              " must be provided in network mapping")
            else:
                error("'network_mappings' must be an array")

        # Virtio drivers
        if 'virtio_win' in data:
            # This is for backward compatibility
            data['install_drivers'] = True
        if 'install_drivers' in data:
            host.check_install_drivers(data)
        else:
            data['install_drivers'] = False

        # Method dependent validation
        data = host.validate_data(data)

        #
        # NOTE: don't use error() beyond this point!
        #

        # Store password(s)
        logging.info('Writing password file(s)')
        if 'vmware_password' in data:
            data['vmware_password_file'] = write_password(
                    data['vmware_password'], password_files)
        if 'rhv_password' in data:
            data['rhv_password_file'] = write_password(data['rhv_password'],
                                                       password_files)
        if 'ssh_key' in data:
            data['ssh_key_file'] = write_password(data['ssh_key'],
                                                  password_files)

        # Create state file before dumping the JSON
        state = {
                'disks': [],
                'internal': {
                    'disk_ids': {},
                    'ports': [],
                    'state_file': state_file,
                    },
                'failed': False,
                }
        try:
            if 'source_disks' in data:
                logging.debug('Initializing disk list from %r',
                              data['source_disks'])
                for d in data['source_disks']:
                    # NOTE: We expect names from virt-v2v/VMware to be UTF-8
                    # encoded. Encoding them here is safer than decoding the
                    # virt-v2v output.
                    state['disks'].append({
                        'path': d.encode('utf-8'),
                        'progress': 0})
                logging.debug('Internal disk list: %r', state['disks'])
                state['disk_count'] = len(data['source_disks'])
            write_state(state)

            # Send some useful info on stdout in JSON
            print(json.dumps({
                'v2v_log': v2v_log,
                'wrapper_log': wrapper_log,
                'state_file': state_file,
            }))

            # Let's get to work
            logging.info('Daemonizing')
            daemonize()
            agent_pid = None
            agent_sock = None
            if data['transport_method'] == 'ssh':
                agent_pid, agent_sock = spawn_ssh_agent(data)
                if agent_pid is None:
                    raise RuntimeError('Failed to start ssh-agent')
            wrapper(host, data, state, v2v_log, virt_v2v_caps, agent_sock)
            if agent_pid is not None:
                os.kill(agent_pid, signal.SIGTERM)
            if not state.get('failed', False):
                state['failed'] = not host.handle_finish(data, state)
        except Exception:
            # No need to log the exception, it will get logged below
            logging.error('An error occured, finishing state file...')
            state['failed'] = True
            write_state(state)
            raise
        finally:
            if state.get('failed', False):
                # Perform cleanup after failed conversion
                logging.debug('Cleanup phase')
                try:
                    host.handle_cleanup(data, state)
                finally:
                    state['finished'] = True
                    write_state(state)

        # Remove password files
        logging.info('Removing password files')
        for f in password_files:
            try:
                os.remove(f)
            except OSError:
                logging.exception('Error while removing password file: %s' % f)

        state['finished'] = True
        write_state(state)

    except Exception:
        logging.exception('Wrapper failure')
        # Remove password files
        logging.info('Removing password files')
        for f in password_files:
            try:
                os.remove(f)
            except OSError:
                logging.exception('Error removing password file: %s' % f)
        # Re-raise original error
        raise

    logging.info('Finished')

# }}}


if __name__ == '__main__':
    main()
