# Ansible Roles

There are many variables that can be configured to tune the setup.
Some are useful only in development environment and some are not really meant
to be changed.

| Variable                       | Default value | Description                                                                                                                           |
| -----------------------------  | ------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| v2v_transport_methods          |               | List of transport methods to configure on the conversion host. Valid values: `vddk`, 'ssh`.                                           |
| v2v_max_concurrent_conversions |               | Override the maximum concurrent conversions per host in ManageIQ configuration.                                                       |
| v2v_vddk_package_name          |               | File name of the .tar.gz package with VDDK library. It is looked for in /tmp.                                                         |
| v2v_vddk_package_url           |               | URL to the VDDK library package (will be downloaded to `/tmp`). Note that the file name must much the one in `v2v_vddk_package_name`. |
| v2v_vddk_override              | false         | Normally the install role is not run if the plugin is already installed. To force the deployment set this variable to `true`.         |
| v2v_ssh_private_key            |               | The private key to use to connect to the VMware host.                                                                                 |
| v2v_checks_override            | false         | The install role does performs some compatibility checks. By setting `v2v_checks_override` to `true` one can disable them.            |
| v2v_yum_check                  | latest        | Can be used to change the requirement on installed packages. Normally we check if the installed packages are at the latest version. This can cause troubles on disconnected or unconfigured systems. In that case the check can be ... by setting the value to `present`. (Since 1.7) |

As the conversion host is used from a ManageIQ appliance, we provide variables
to configure the conversion host records in ManageIQ, as well as the conversion
host with ManageIQ providers configuration.

| Variable                | Default value | Description                                                                              |
| ----------------------- | ------------- | ---------------------------------------------------------------------------------------- |
| manageiq_url            |               | Base URL for ManageIQ appliance with API role                                            |
| manageiq_username       | admin         | Username to connect to ManageIQ                                                          |
| manageiq_password       | smartvm       | Password to connect to ManageIQ                                                          |
| manageiq_validate_certs | true          | Whether to validate certificate of ManageIQ server                                       |
| manageiq_providers      |               | List of definitions of ManageIQ providers. Each provider is a dictionary described below |

A ManageIQ provider has the following attributes:

| Attribute                 | Description                                                                                 |
| ------------------------- | ------------------------------------------------------------------------------------------- |
| name                      | Name of the provider in CloudForms. Accepts spaces and upper/lower case.                    |
| hostname                  | Hostname of the provider endpoint.                                                          |
| connection_configurations | A list of additional endpoint configuration items. The possible values are described below. |

The `connection_configurations` for Red Hat Virtualization has only one
endpoint, whose role is `default`. For that endpoint, we can specify whether we
want to verify the SSL certificate (`verify_ssl`) and eventually provide a CA
chain (`certificate_authority`). The content of the CA chain is available in
`/etc/pki/ovirt-engine/apache-ca.pem` on the RHV Manager.

The `connection_configurations` for OpenStack also has a single endpoint. We
can specify if connection is secure: `non-ssl`, `ssl-without-validation` or
`ssl` . In the case of `ssl`, we can provide a CA chain
(`certificate_authority`). The content of the CA chain can be built from the
undercloud CA (/etc/pki/ca-trust/source/anchors/undercloud-cacert.pem) and
the overcloud CA (/etc/pki/ca-trust/source/anchors/overcloud-cacert.pem).


## Example inventory

```yaml
all:
  vars:
  hosts:
    chost1.example.com:
      v2v_host_type: rhv
      v2v_transport_methods:
        - vddk
        - ssh
      v2v_max_concurrent_conversions: 20
      manageiq_provider_name: Shiny RHV
    chost2.example.com:
      v2v_host_type: openstack
      v2v_transport_methods:
        - vddk
      manageiq_provider_name: Brilliant OpenStack
  vars:
    v2v_repo_rpms_name: "v2v-nbdkit-rpms"
    v2v_repo_rpms_url: "http://content.example.com/v2v-nbdkit-rpms"
    v2v_repo_srpms_name: "v2v-nbdkit-src-rpms"
    v2v_repo_srpms_url: "http://content.example.com/v2v-nbdkit-src-rpms"
    v2v_vddk_package_name: "VMware-vix-disklib-6.5.2-6195444.x86_64.tar.gz"
    v2v_vddk_package_url: "http://content.example.com/{{ v2v_vddk_package_name }}"
    v2v_ssh_private_key: |
      -----BEGIN RSA PRIVATE KEY-----
      b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAlwAAAAdzc2gtcn
      NhAAAAAwEAAQAAAIEAuUPezWEyOS+KbDj+GWjvQUjgugMvPREhHsTuqhvNs3rU7qkQYit6
      y8J5PFiuQAViDNvhjyESBh1QwT45utZUkUD0wrHJ/lrxmM9NKaDaYr/rNM97Gkao8Jp9aq
      /1IfQXYrlxIcdOpTTQRIib1f0QR1Rgo7Ekz0tNXvt3AXbqo98AAAIYq1X3AatV9wEAAAAH
      c3NoLXJzYQAAAIEAuUPezWEyOS+KbDj+GWjvQUjgugMvPREhHsTuqhvNs3rU7qkQYit6y8
      J5PFiuQAViDNvhjyESBh1QwT45utZUkUD0wrHJ/lrxmM9NKaDaYr/rNM97Gkao8Jp9aq/1
      IfQXYrlxIcdOpTTQRIib1f0QR1Rgo7Ekz0tNXvt3AXbqo98AAAADAQABAAAAgQCBjwQVrn
      4X3bY4vpZ8IJUIm7WEf8ueMgduZBvfXDg65pBYImTxsiRasDJmUEHzRZBvG6melWrsWb3q
      leB7V32lMNxXmFAORELLjo0LQUIROH+YjETxmEzaAvGK/PfNDTXuTKFlRp2+VMJIF+S0V/
      S4AsJ6YZkxH78RoexiYHFYMQAAAEEAtGPkFquU/Qy4POAf9HOb4Xe+dgMgENs+rZV3gzeD
      7wnQP1M7sZwGKhde+BlhiuSgkUW6+2Am/ui7nvOwt+9begAAAEEA7r1VsA+y7tljxwHWYT
      8lx5NIfFCfIaB3VpvlBltBxI0T56qMBxVIPoEgCcFL3CVtRLZ/KukgJKiXEk/EREgNFwAA
      AEEAxqjQUreggg6tzLrrDOchATWDxZH/KBpOpalrWc9afbDAbiOWidR9lex+X+pXHa1kYM
      ++vZcXPGeWRqLYHReseQAAAB9mZHVwb250QHNhbWFlbC5ob21lLmV2ZW5pdC5pbmZvAQI=
      -----END RSA PRIVATE KEY-----
    manageiq_url: "https://miq.example.com"
    manageiq_username: "admin"
    manageiq_password: "smartvm"
    manageiq_zone_id: "42000000000001"
    manageiq_providers:
      - name: "Shiny RHV"
        hostname: "rhvm.example.com"
        connection_configurations:
          - endpoint:
              role: "default"
              verify_ssl: true
              certificate_authority: |
                -----BEGIN CERTIFICATE-----
                MIIDoDCCAoigAwIBAgIBATANBgkqhkiG9w0BAQsFADA9MRswGQYDVQQKDBJWMlYu
                Qk9TLlJFREhBVC5DT00xHjAcBgNVBAMMFUNlcnRpZmljYXRlIEF1dGhvcml0eTAe
                Fw0xODAzMTIwOTQ2MzBaFw0zODAzMTIxMDQ2MzBaMD0xGzAZBgNVBAoMElYyVi5C
                T1MuUkVESEFULkNPTTEeMBwGA1UEAwwVQ2VydGlmaWNhdGUgQXV0aG9yaXR5MIIB
                IjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu09lHK9LJFGxZMES9GznXLyb
                Nc7Lb7LUH+nYO8bhfYKeV6DgZFiOuOOonlYVHRSj38IvLegwuGVhwHgl5/C2KEG0
                C8lZxCX8roaYPs3zJKnteiLBsEgrni/mcL7cV8fDfzt4ZciZZ7FRUX0AncRIyzTg
                G3bqT3VPOWnR32J0686FaVqyNUkvtqHbIziEqVi+mSvHLt3X0mXobYAYhORZuiGo
                U3WCdjEbQBdphlna/USNHoqvXKgH1Lchm5NUvGFq3YpBedULPgudMx5+4rZV6rb3
                +ij+IX+yuY1Ncdu55uJeN71vPcVQy26uBZKsKkHz+ApFSbUNctE+UfZanysQswID
                AQABo4GqMIGnMB8GA1UdIwQYMBaAFNSP2ggYA8NgnELbC9547QUSEitaMA8GA1Ud
                EwEB/wQFMAMBAf8wDgYDVR0PAQH/BAQDAgHGMB0GA1UdDgQWBBTUj9oIGAPDYJxC
                2wveeO0FEhIrWjBEBggrBgEFBQcBAQQ4MDYwNAYIKwYBBQUHMAGGKGh0dHA6Ly9p
                cGEtY2EudjJ2LmJvcy5yZWRoYXQuY29tL2NhL29jc3AwDQYJKoZIhvcNAQELBQAD
                ggEBADK4JOxl+Fl5RSDsqlOqsQrlZ6CJ86Y0llJQZhV32ioCKSO5ZnPlTjGhJJxf
                urZ+cvDeRDFKSb5n8cyRV2ycPcUXsTjWQQBr5TXmQWbBR4dEDavL+oOF5H4wKFVv
                q6W7gOS4JFfNJ9/vZulaEJoxV2JEJ4oalVTriTRn4LA6MZLaAL9sbNZplQ9N5vEr
                Iyc+rL4KW2wp6TfhH2qc6uT1c9WyLEeWuN58/+MP8ux4eS+U79usmacsmZ0bbsqr
                sL/aCydm+Mj73hZrx12te065/f1VHR0Kly8iLKo7ByOsvXGCcYCQljV1Ho2x9ZQU
                19n+csCTKX0uu6MTLAkDejfM/Ws=
                -----END CERTIFICATE-----
      - name: "Brilliant OpenStack"
        hostname: "openstack.example.com"
        connection_configurations:
          - endpoint:
              role: "default"
              security_protocol: "ssl"
              certificate_authority: |
                -----BEGIN TRUSTED CERTIFICATE-----
                MIIDNzCCAh8CAQEwDQYJKoZIhvcNAQELBQAwYjELMAkGA1UEBhMCVVMxCzAJBgNV
                BAgMAk5DMRAwDgYDVQQHDAdSYWxlaWdoMRAwDgYDVQQKDAdSZWQgSEF0MQswCQYD
                VQQLDAJRRTEVMBMGA1UEAwwMMTkyLjE2OC4yNC4yMB4XDTE4MTEwODIyMzg0MVoX
                DTE5MTEwODIyMzg0MVowYTELMAkGA1UEBhMCVVMxCzAJBgNVBAgMAk5DMRAwDgYD
                VQQHDAdSYWxlaWdoMRAwDgYDVQQKDAdSZWQgSEF0MQswCQYDVQQLDAJRRTEUMBIG
                A1UEAwwLMTAuOC4xOTcuODQwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIB
                AQDCh0IIszxUjiR5YiBZDzYWFKircfiKXgw2o9K5V6J5Aqflnm2tUHl1jtucAwsk
                EoDIgc9Cf8UVS8gw5KBIFxJKnILhu1HGud/jrNtNZuBOq1WeMa8suSKSOg1tvH+k
                ltbzLMBFBz1x/AnzUkadpQQeaw58pP8kQIT/MTkw9i+yEwq2tjwer+806tWMpm0e
                eG27UbCVpel/ex6WTR5sUe0lmoRoVwpBkC0WQsip9Ly8aY0ZeHgnWIeNvf52olwW
                hEl7LhpRMUH0E24uEAo7+ChiNp7q640L0QWcEDfTYEwTyS+zy1/n0S0EWohWLyxR
                B7GDr+4z+dgztGCjKtKmTN2fAgMBAAEwDQYJKoZIhvcNAQELBQADggEBAIBMl35D
                onOMr1ZuKFMnl/x3LhJihRL5c1XZ2VTPx7P6fOeEoWwocuqW40BE+HLMXX9K4dUI
                fYEi/vRSh/8Obcirvobztl2KPripo1PXOLx82a8eTpQFubELqBKVVSUQkIIKpyIW
                Itbf/+4I08j9hXG1XGZtla05SEx9je5ntZI9DwsNRIe3ZNWeEoTZnG5cpXKoTuiv
                ZSBZV5uygZ6yGv7hnoqVRNXZP4OKE0ZdVt1TxbO0dBPjav6NdTpi7e9ZmVGKv9Xi
                drf/14FoGeDsU2zXLQ/UAqlzaAqx1NAtp99wnX3yI2dXJzGpVXdl0SJU6Hi5M+32
                PFjCzC1Et4Yl6sUwDQwLMTAuOC4xOTcuODQ=
                -----END TRUSTED CERTIFICATE-----
                -----BEGIN TRUSTED CERTIFICATE-----
                MIIDlzCCAn+gAwIBAgIJAOP7AaT7dsLYMA0GCSqGSIb3DQEBCwUAMGIxCzAJBgNV
                BAYTAlVTMQswCQYDVQQIDAJOQzEQMA4GA1UEBwwHUmFsZWlnaDEQMA4GA1UECgwH
                UmVkIEhBdDELMAkGA1UECwwCUUUxFTATBgNVBAMMDDE5Mi4xNjguMjQuMjAeFw0x
                ODExMDUyMTE3NTFaFw0xOTExMDUyMTE3NTFaMGIxCzAJBgNVBAYTAlVTMQswCQYD
                VQQIDAJOQzEQMA4GA1UEBwwHUmFsZWlnaDEQMA4GA1UECgwHUmVkIEhBdDELMAkG
                A1UECwwCUUUxFTATBgNVBAMMDDE5Mi4xNjguMjQuMjCCASIwDQYJKoZIhvcNAQEB
                BQADggEPADCCAQoCggEBAODRYemzQhGx2+8t0Peru6BEv2EFpxGKbav5p+6NzFXb
                50ccUIXA59+5vEEUr8EF8aCJuizBjAskPXwAT89qlbrsxKfN/r/xFOGvMkQ3xA2S
                ucnZCZXaVGkk/KC3VzPrd3atmPHWmAjTb37m4b1vKBRC9zh1F1l2CEyb31Eku4br
                gi4PwqoUQWIwiXPhD88YLuRKxdc079j7NRICBfJN68tzK81TW9cCQiOR7PdMuPzm
                h9nyNfYDeuGOuIFbpmL+8cLCofdMlyKtz/v+Y8s5bTtEf0ETG3qLYXskWM5nYYK+
                AkdKV3yZDrBha1X9Qo8wRcNZUas0kycXtZOXspPQ9AkCAwEAAaNQME4wHQYDVR0O
                BBYEFJzqK4CnpGbnQJIsN2te/jndZk2yMB8GA1UdIwQYMBaAFJzqK4CnpGbnQJIs
                N2te/jndZk2yMAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEBAJs+irLk
                osXnAqN8HwCp8NFGo2armdb/HE7v+qUanHRFfxDJJ70KhTM2gEi732u19oxhpgJP
                LNj40fC6U6A17oeNzGk+U75cOnbHY0Wovdo/2E8n508zsg0f+h8170QCKwf1qqd+
                o+AbxDIH6C262pF4AGjYQxK302Xj4Te+XckQa6nIX4xk1xJeHEzlxfBcV3h6BQH8
                sVqekffwgMFam9A66Ovcx8QgzZ2HpVnuq/CMY/sUxp0dK5PsnpKbUm6UCqaXigY7
                hgpqdqIdwkeR+c+fbYZKXBOBotCcmEXoHuIlZ9GhIti7gwSBSRWEjkPEL2j8R/zK
                k2ikyNbbVRx/13AwDgwMMTkyLjE2OC4yNC4y
                -----END TRUSTED CERTIFICATE-----
```
