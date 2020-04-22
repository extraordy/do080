lang en_US
keyboard us
timezone America/New_York --isUtc

rootpw --lock

#platform x86, AMD64, or Intel EM64T
reboot
text
cdrom
bootloader --location=mbr --append="rhgb quiet crashkernel=auto"
zerombr
clearpart --all --initlabel
autopart
auth --passalgo=sha512 --useshadow
selinux --enforcing
firewall --enabled --ssh
firstboot --disable


%post --log=/root/ks-post-v2v.log --erroronfail
# Add RHEL OSP repos before Image build
%end


%packages
ansible
ovirt-ansible-v2v-conversion-host

# tasks/install.yml
nbdkit  # nbdkit source requires RHEL 7.6 or RHV channel
nbdkit-plugin-python2
virt-v2v

# tasks/install-openstack.yml
python-six
python2-openstackclient
virtio-win
%end
