# Virt-v2v Wrapper

The script shields the caller from complexities involved in starting virt-v2v
on oVirt/RHV host. It daemonizes to the background and monitors the progress
of the conversion, providing the status information in a state file. This
allows for asynchronous conversion workflow.

The expected usage is as follows:

1)  *wrapper start*: client runs the wrapper; at the moment there are no
    command line arguments and everything is configured by JSON data presented
    on stdin.

2)  *initialization*: wrapper read JSON data from stdin, parses and validates
    the content; based on the situation it may also change the effective user
    to a non-root account

3)  *daemonization*: wrapper writes to stdout simple JSON containing paths to
    wrapper log file (`wrapper_log`), virt-v2v log file (`v2v_log`) and to the
    state file (`state_file`) that can be used to monitor the progress; after
    that it forks to the background

4)  *conversion*: finally, virt-v2v process is executed; wrapper monitors its
    output and updates the state file on a regular basis

5)  *finalization*: when virt-v2v terminates wrapper updates the state file
    one last time and exits


## Input Data

This section describes various keys understood by the wrapper in JSON on
input. Keys are mandatory unless explicitly stated otherwise.

General information:

* `vm_name`: name of the VM to import. In case of `ssh` transport method this
  is an URI containing the host and path to the VM files, e.g.
  `ssh://root@1.2.3.4/vmfs/volumes/datastore/tg-mini/tg-mini.vmx`.

* `output_format`: one of `raw`, or `qcow2`; default is `raw` if not specified

* `transport_method`: type of transport to use; supported methods are `ssh` and
  `vddk`.

For `vddk` the following keys need to be specified:

* `vmware_uri`: libvirt URI of the source hypervisor

* `vmware_password`: password used when connecting to the source hypervisor

* `vmware_fingerprint`: fingerprint of SSL certificate on the source
  hypervisor (also called thumbprint)

For `ssh` method there are no other information necessary. Optionaly the
following can be specified:

* `ssh_key`: optional, private part of SSH key to use. If this is not provided
  then keys in ~/.ssh directory are used.

Output configuration: reffer to the section [Output
configuration](#output-configuration) below.

Miscellaneous:

* `source_disks`: optional key containing list of disks in the VM; if specified
  it is used to initialize progress information in the state file

* `network_mappings`: optional key containing list of network mappings; if
   specified, it is used to connect the VM's NICs to the destination networks
   during the conversion using virt-v2v `--bridge` option.

* `virtio_win`: optional key containing path to virtio-win ISO image; this is
  useful for installing Windows drivers to the VM during conversion. It may be
  either absolute path or only a filename in which case path to ISO domain is
  auto-detected.

* `install_drivers`: optional key whether to install Windows drivers during
  conversion, default is `false`. If `install_drivers` is `true` and
  `virtio_win` is not specified, wrapper attempts to automatically select best
  ISO from the ISO domain. Note that when no ISO is found this does not lead to
  failed conversion. Just no drivers will be installed in this case. This is
  different from situation when `virtio_win` is specified but points to
  non-existing ISO, which is an error.

* `allocation`: optional key specifying the allocation type to use; possible
  values are `preallocated` and `sparse`.

Example:

    {
        "export_domain": "storage1.example.com:/data/export-domain",
        "vm_name": "My_Machine",

        "transport_method": "vddk",
        "vmware_fingerprint": "1A:3F:26:C6:DC:2C:44:88:AA:33:81:3C:18:6E:5D:9F:C0:EE:DF:5C",
        "vmware_uri": "esx://root@10.2.0.20?no_verify=1",
        "vmware_password": "secret-password",

        "source_disks": [
            "[dataStore_1] My_Machine/My_Machine_1.vmdk",
            "[dataStore_1] My_Machine/My_Machine_2.vmdk"
        ],
        "network_mappings": [
            {
                "source": "networkA1",
                "destination": "networkA2"
            },
            {
                "source": "networkX1",
                "destination": "networkX2"
            }
        ],
        "virtio_win": "virtio-win-0.1.141.iso"
    }

## Output configuration

There is no configuration key specifying the type of output. Rather the output
method is chosen depending on the keys present. If there are keys defining
multiple output modes the first one is selected base on the order of
precedence. The order is following:

1)  oVirt API upload

2)  export domain

### oVirt API upload

To select oVirt API upload method add `rhv_url` to the configuraton. Together
with `rhv_url` some other keys need to be also specified.

* `rhv_url`: URL to the oVirt API endpoint.

* `rhv_password`: password used to authorize to API

* `rhv_cluster`: name of the target cluster

* `rhv_storage`: name of the target storage domain

* `rhv_cafile`: optional on VDSM host; path to the CA certificate. If the key
  is not specified wrapper looks for the certificate at the default VDSM
  location.

* `insecure_connection`: optional, whether to verify peer certificates. For now
  used only when connecting to oVirt/RHV. Default is `false`.

Example:

    {
        ...
        "rhv_url": "https://ovirt.example.com/ovirt-engine/api",
        "rhv_password": "secret-password",
        "rhv_cluster": "Default",
        "rhv_storage": "data",
        "rhv_cafile": "/etc/pki/vdsm/certs/cacert.pem",
        "insecure_connection": true
    }


### Export domain

To request conversion into export domain add the following key to the
configuration:

* `export_domain`: specify path to NFS share in the format `<hostname>:<path>`


## State File Format

State file is a JSON file. Its content changes as the conversion goes through
various stages. With it also the keys present in the file.

Once virt-v2v is executed the state file is created with the following keys:

* `started`: with value `true`

* `pid`: the process ID of virt-v2v. This can be used to kill the process and
  terminate the conversion. In this case, once virt-v2v terminates (with
  non-zero return code) the wrapper immediately terminates too.

* `disks`: array of progress per each disk. The value is either empty list or
  a list of objects initialized from `source_disks` passed to the wrapper. If
  no `source_disks` is specified, the `disks` list is constructed incrementally
  during the conversion process.

* `disk_count`: the number of disks that will be copied. Initially zero or
  number of disks in `source_disks`. When virt-v2v starts copying disks, the
  value is updated to match the count of disks virt-v2v will actually copy.
  Note that the values does not have to represent the length of `disks` array!
  If `source_disks` is not specified or contains invalid values length of
  `disks` can be smaller or larger than `disk_count`.

When virt-v2v gets past the initialization phase and starts copying disks the
wrapper updates the progress for each disk in the `disks` list. Each item in
the list contains the following keys:

* `path`: the path description of the disk as the backend sees it

* `progress`: the percentage of the disk copied, in the range from 0 to 100 (as
  numeric)

When virt-v2v finishes the state is updated with the following keys:

* `return_code`: return code of virt-v2v process. As usual 0 means the process
  terminated successfully and any non-zero value means an error. Note however,
  that the value should not be used to check if conversion succeeded or failed.
  (See below.)

Right before the wrapper terminates it updates the state with:

* `finished`: with value `true`

* `failed`: with value `true` if the conversion process failed. If everything
  went OK, this key is not present. Existence of this key is the main way how
  to check whether the conversion succeeded or not.
