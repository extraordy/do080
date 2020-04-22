oVirt Repositories
==================

The `ovirt.repositories` role is used to set the repositories required for
oVirt engine or host installation. By default it copies content of
/etc/yum.repos.d/ to /tmp/repo-backup-{{timestamp}}, so it's easy to undo that operation.

Note
----
Please note that when installing this role from Ansible Galaxy you are instructed to run following command:

```bash
$ ansible-galaxy install ovirt.repositories
```

This will download the role to the directory with the same name as you specified on the
command line, in this case `ovirt.repositories`. But note that it is case sensitive, so if you specify
for example `OVIRT.repositories` it will download the same role, but it will add it to the directory named
`OVIRT.repositories`, so you later always have to use this role with upper case prefix. So be careful how
you specify the name of the role on command line.

For the RPM installation we install three legacy names `oVirt.repositories`, `ovirt.repositories` and `ovirt-repositories`.
So you can use any of these names. This documentation and examples in this repository are using name `ovirt.repositories`.
`oVirt.repositories` and `ovirt-repositories` role names are deprecated.

Requirements
------------

 * Ansible version 2.9

Role Variables
--------------

| Name                                       | Default value         |  Description                              |
|--------------------------------------------|-----------------------|-------------------------------------------|
| ovirt_repositories_ovirt_release_rpm       | UNDEF                 | URL of oVirt release package, which contains required repositories configuration. |
| ovirt_repositories_use_subscription_manager| False                 | If true it will use repos from subscription manager and the value of <i>ovirt_repositories_ovirt_release_rpm</i> will be ignored. |
| ovirt_repositories_ovirt_version           | 4.3                   | oVirt release version (Supported versions [4.1, 4.2, 4.3]). Will be used to enable the required repositories in case <i>ovirt_repositories_use_subscription_manager</i> is set. |
| ovirt_repositories_target_host             | engine                | Type of the target machine, which should be one of [engine, host, rhvh]. This parameter takes effect only in case <i>ovirt_repositories_use_subscription_manager</i> is set to True. If incorrect version or target is specified no repositories are enabled. |
| ovirt_repositories_rh_username             | UNDEF                 | Username to use for subscription manager. |
| ovirt_repositories_rh_password             | UNDEF                 | Password to use for subscription manager. |
| ovirt_repositories_pool_ids                | UNDEF                 | List of pools ids to subscribe to. |
| ovirt_repositories_pools                   | UNDEF                 | Specify a list of subscription pool names. Use <i>ovirt_repositories_pool_ids</i> instead if possible, as it is much faster. |
| ovirt_repositories_repos_backup_path       | /tmp/repo-backup-{{timestamp}} | Directory to backup the original repositories configuration |
| ovirt_repositories_force_register          | False                 | Bool to register the system even if it is already registered. |
| ovirt_repositories_rhsm_server_hostname    | UNDEF                 | Hostname of the RHSM server. By default it's used from rhsm configuration. |


Dependencies
------------

No.

Example Playbook
----------------

```yaml
---
- name: Setup repositories using oVirt release package
  hosts: localhost

  vars:
    ovirt_repositories_ovirt_release_rpm: http://resources.ovirt.org/pub/yum-repo/ovirt-master-release.rpm

  roles:
    - role: ovirt.repositories

- vars_files:
    # Contains encrypted `username` and `password` variables using ansible-vault
    - passwords.yml

- name: Setup repositories using Subscription Manager
  hosts: localhost

  vars:
    ovirt_repositories_use_subscription_manager: True
    ovirt_repositories_force_register: True
    ovirt_repositories_rh_username: "{{ovirt_repositories_rh_username}}"
    ovirt_repositories_rh_password: "{{ovirt_repositories_rh_password}}"
    # The following pool IDs are not valid and should be replaced.
    ovirt_repositories_pool_ids:
      - 0123456789abcdef0123456789abcdef
      - 1123456789abcdef0123456789abcdef

  roles:
    - role: ovirt.repositories


- name: Setup repositories using Subscription Manager pool name
  hosts: localhost

  vars:
    ovirt_repositories_use_subscription_manager: True
    ovirt_repositories_force_register: True
    ovirt_repositories_rh_username: "{{ovirt_repositories_rh_username}}"
    ovirt_repositories_rh_password: "{{ovirt_repositories_rh_password}}"
    ovirt_repositories_pools:
      - "Red Hat Cloud Infrastructure, Premium (2-sockets)"

  roles:
    - role: ovirt.repositories
```

License
-------

Apache License 2.0
