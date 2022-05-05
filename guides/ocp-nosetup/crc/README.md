# OpenShift Local - Un cluster all in one!

OpenShift Local (precedentemente conosciuto come CodeReady Containers), è un progetto che ci permette di andare ad installare una macchina virtuale compatta che comprende una installazione minimale di un cluster OpenShift all-in-one, con caratteristiche identiche all'installazione reale, ma con il vantaggio di richiedere una quantità di risorse decisamente inferiore, oltre a risparmiarci l'effort di dover eseguire una installaizone vera e propria, con conseguenti configurazioni a livello di rete, storage e quant'altro.
Un setup di questo tipo è ottimo per iniziare a muovere i primi passi, avendo a disposizione un ambiente funzionante, disponibile e pronto all'installazione su qualsiasi sistema operativo supportato finora.

Per maggiori informazioni o per la risoluzione dei problemi più comuni:

- [homepage di OpenShift Local](https://console.redhat.com/openshift/create/local)
- [documentazione ufficiale di OpenShift Local](https://access.redhat.com/documentation/en-us/red_hat_openshift_local/)

## Download link:

**Linux - libvirt**  
https://mirror.openshift.com/pub/openshift-v4/clients/crc/latest/crc-linux-amd64.tar.xz

**MacOS - Hyperkit**  
https://mirror.openshift.com/pub/openshift-v4/clients/crc/latest/crc-macos-amd64.pkg

**Windows - HyperV**  
https://mirror.openshift.com/pub/openshift-v4/clients/crc/latest/crc-windows-installer.zip

## Tabella di compatibilità

|  Sistema Operativo | Versione supportata  |
| :------------ | :------------ |
| Windows  | Windows 10 Professional Fall Creators Update, versione 1709 o successiva |
| Mac | macOS, versione 10.14 Mojave o successiva<br /> :warning: l'architettura M1 non è ancora supportata |
| Linux  | Red Hat Enterprise Linux/CentOS 7.5 o successivi </br> le ultime due release stabili di Fedora </br> Ubuntu 18.04 LTS, Debian 10 o successivi non sono ufficialmente supportati, e potrebbero richiedere l'installazione di software aggiuntivo |

I requisiti di sistema, invece, sono i seguenti:

- 4 virtual CPU (vCPU)
- 9 GB di memoria
- 35 GB di storage disponibili

>### :warning: NOTA BENE
>
>L'installer andrà automaticamente a creare una virtual machine. Non è necessario quindi creare alcuna vm in precedenza. Il setup nested (con virtual machine annidate) non è supportato.

# Installazione

In questa sezione andremo a coprire l'installazione della piattaforma in ambiente Linux, Windows e Mac. 

Durante l'installazione, sarà richiesta una chiave (Pull Secret), che servirà per il download di contenuti dai registry Red Hat per l'utilizzo del nostro cluster.

Questa può essere reperita alla pagina https://cloud.redhat.com/openshift/create/local, previo login con utenza Red Hat Developer, dove potrete utilizzare il pulsante "Copy pull secret" per copiarlo nella clipboard ed incollarlo direttamente nella command line  
![](images/pull-secret.png)

## Installazione su Windows

Una volta eseguito il download seguendo il link indicato, ci troveremo con un file compresso che andremo ad estrarre:  
![](images/win_download.png)

Una volta decisa la location del download, all’interno troveremo la directory che comprende l'eseguibile **crc** che andremo ad utilizzare.

Per andarlo ad eseguire, apriamo il prompt dei comandi:  
![](images/win_cmd.png)

Spostiamoci nella directory dove abbiamo estratto il nostro file, nel mio caso nella directory "Downloads\crc-windows-amd64\crc-windows-1.8.0-amd64":

`cd "Downloads\crc-windows-amd64\crc-windows-1.8.0-amd64"`

Per inizializzare la macchina virtuale, è necessario utilizzare il comando 'crc setup'

    C:\Users\alex\Downloads\crc-windows-amd64\crc-windows-1.8.0-amd64>crc setup
    INFO Checking if oc binary is cached
    INFO Checking if podman remote binary is cached
    INFO Checking if CRC bundle is cached in '$HOME/.crc'
    INFO Checking if running as normal user
    INFO Checking Windows 10 release
    INFO Checking if Hyper-V is installed and operational
    INFO Checking if user is a member of the Hyper-V Administrators group
    INFO Checking if Hyper-V service is enabled
    INFO Checking if the Hyper-V virtual switch exist
    INFO Found Virtual Switch to use: Default Switch
    Setup is complete, you can now run 'crc start' to start the OpenShift cluster


Una volta terminata la fase di setup, è possibile avviare la predisposizione della macchina virtuale che servirà il nostro cluster Openshift!

    C:\Users\alex\Downloads\crc-windows-amd64\crc-windows-1.8.0-amd64>crc start
    INFO Checking if oc binary is cached
    INFO Checking if podman remote binary is cached
    INFO Checking if running as normal user
    INFO Checking Windows 10 release
    INFO Checking if Hyper-V is installed and operational
    INFO Checking if user is a member of the Hyper-V Administrators group
    INFO Checking if Hyper-V service is enabled
    INFO Checking if the Hyper-V virtual switch exist
    INFO Found Virtual Switch to use: Default Switch
    ? Image pull secret [? for help] 

A questo punto, l'installer ci sta chiedendo di inserire una chiave (Pull Secret) che occorre inserire per il download delle immagini necessarie.

Una volta inserita, l'installazione proseguirà:


    INFO Extracting bundle: crc_hyperv_4.3.8.crcbundle ...
    INFO Checking size of the disk image C:\Users\ale\.crc\cache\crc_hyperv_4.3.8\crc.vhdx ...
    INFO Creating CodeReady Containers VM for OpenShift 4.3.8...
    INFO Verifying validity of the cluster certificates ...
    INFO Will run as admin: add dns server address to interface vEthernet (Default Switch)
    INFO Check internal and public DNS query ...
    INFO Check DNS query from host ...
    INFO Copying kubeconfig file to instance dir ...
    INFO Adding user's pull secret ...
    INFO Updating cluster ID ...
    INFO Starting OpenShift cluster ... [waiting 3m]
    INFO
    INFO To access the cluster, first set up your environment by following 'crc oc-env' instructions
    INFO Then you can access it by running 'oc login -u developer -p developer https://api.crc.testing:6443'
    INFO To login as an admin, run 'oc login -u kubeadmin -p kKdPx-pjmWe-b3kuu-jeZm3 https://api.crc.testing:6443'
    INFO
    INFO You can now run 'crc console' and use these credentials to access the OpenShift web console
    Started the OpenShift cluster
    WARN The cluster might report a degraded or error state. This is expected since several operators have been disabled to lower the resource usage. For more information, please consult the documentation

Al termine dell'installazione viene generata una password per l'utente developer (pass: developer) e per l'utente amministratore **kubeadmin** che dovrete salvare per poter accedere al vostro cluster!


## Installazione su Linux

Affinchè sia possibile installare OpenShift Local su una macchina Linux, è necessario che siano verificate ed installate le sue uniche dipendenze, **libvirt** e **NetworkManager**.

Di seguito una piccola tabella dove troverete i comandi da eseguire a seconda della distribuzione in uso.

| Distribuzione Linux  |  Installazione dei requisiti |
| :------------ | :------------ |
| Fedora  | sudo dnf install NetworkManager  |
| Red Hat Enterprise Linux/CentOS  |  su -c 'yum install NetworkManager' |
| Debian/Ubuntu  | sudo apt install qemu-kvm libvirt-daemon libvirt-daemon-system network-manager  |

L'installazione è veramente semplice, in quanto l'installer si presenta come un'unica entità che andremo ad eseguire e sfrutterà le risorse di sistema per poter funzionare.

Una volta eseguito il download, ci ritroveremo con un file da estrarre, che andremo a scompattare:

    [alex@pollos Scaricati]$ tar -xvf crc-linux-amd64.tar.xz 
    crc-linux-1.8.0-amd64/
    crc-linux-1.8.0-amd64/LICENSE
    crc-linux-1.8.0-amd64/doc.pdf
    crc-linux-1.8.0-amd64/crc
    [alex@pollos Scaricati]$ cd crc-linux-1.8.0-amd64/

Una volta nella directory, potrete invocare il comando 'setup' dell'utility crc per installare la nostra VM:

    [alex@pollos crc-linux-1.8.0-amd64]$ ./crc setup
    INFO Checking if oc binary is cached              
    INFO Checking if CRC bundle is cached in '$HOME/.crc' 
    INFO Unpacking bundle from the CRC binary         
    INFO Checking if running as non-root              
    INFO Checking if Virtualization is enabled        
    INFO Checking if KVM is enabled                   
    INFO Checking if libvirt is installed             
    INFO Checking if user is part of libvirt group    
    INFO Checking if libvirt is enabled               
    INFO Checking if libvirt daemon is running        
    INFO Checking if a supported libvirt version is installed 
    INFO Checking if crc-driver-libvirt is installed  
    INFO Checking for obsolete crc-driver-libvirt     
    INFO Checking if libvirt 'crc' network is available 
    INFO Checking if libvirt 'crc' network is active  
    INFO Checking if NetworkManager is installed      
    INFO Checking if NetworkManager service is running 
    INFO Checking if /etc/NetworkManager/conf.d/crc-nm-dnsmasq.conf exists 
    INFO Checking if /etc/NetworkManager/dnsmasq.d/crc.conf exists 
    Setup is complete, you can now run 'crc start' to start the OpenShift cluster

Una volta terminata la fase di setup, è possibile avviare la predisposizione della macchina virtuale che servirà il nostro cluster Openshift!

    [alex@pollos crc-linux-1.8.0-amd64]$ ./crc start
    INFO Checking if oc binary is cached              
    INFO Checking if podman remote binary is cached   
    INFO Checking if running as non-root              
    INFO Checking if Virtualization is enabled        
    INFO Checking if KVM is enabled                   
    INFO Checking if libvirt is installed             
    INFO Checking if user is part of libvirt group    
    INFO Checking if libvirt is enabled               
    INFO Checking if libvirt daemon is running        
    INFO Checking if a supported libvirt version is installed 
    INFO Checking if crc-driver-libvirt is installed  
    INFO Checking if libvirt 'crc' network is available 
    INFO Checking if libvirt 'crc' network is active  
    INFO Checking if NetworkManager is installed      
    INFO Checking if NetworkManager service is running 
    INFO Checking if /etc/NetworkManager/conf.d/crc-nm-dnsmasq.conf exists 
    INFO Checking if /etc/NetworkManager/dnsmasq.d/crc.conf exists 
    ? Image pull secret [? for help] 

A questo punto, l'installer ci sta chiedendo di inserire una chiave (Pull Secret) che occorre inserire per il download delle immagini necessarie.

Il resto del processo è qualcosa di simile, al termine dell'installazione viene generata una password per l'utente developer (pass: developer) e l'utente amministratore **kubeadmin** che dovrete salvare per poter accedere al vostro cluster!

    INFO Loading bundle: crc_libvirt_4.3.8.crcbundle ... 
    INFO Checking size of the disk image /home/alex/.crc/cache/crc_libvirt_4.3.8/crc.qcow2 ... 
    INFO Creating CodeReady Containers VM for OpenShift 4.3.8... 
    INFO Verifying validity of the cluster certificates ... 
    INFO Check internal and public DNS query ...      
    INFO Check DNS query from host ...                
    INFO Copying kubeconfig file to instance dir ...  
    INFO Adding user's pull secret ...                
    INFO Updating cluster ID ...                      
    INFO Starting OpenShift cluster ... [waiting 3m]  
    INFO                                              
    INFO To access the cluster, first set up your environment by following 'crc oc-env' instructions 
    INFO Then you can access it by running 'oc login -u developer -p developer https://api.crc.testing:6443' 
    INFO To login as an admin, run 'oc login -u kubeadmin -p kKdPx-pjmWe-b3kuu-jeZm3 https://api.crc.testing:6443' 
    INFO                                              
    INFO You can now run 'crc console' and use these credentials to access the OpenShift web console 
    Started the OpenShift cluster
    WARN The cluster might report a degraded or error state. This is expected since several operators have been disabled to lower the resource usage. For more information, please consult the documentation 


## Installazione su MacOS

Una volta eseguito il download seguendo il link indicato, ci troveremo con un file compresso che andremo ad estrarre, semplicemente cliccandoci sopra, dalla finestra del browser. Questo creerà una directory estratta, nella cartella dove è stato scaricato.

All'interno della directory, sarà estratto il file crc che andremo ad utilizzare per inizializzare ed utilizzare la nostra macchina virtuale.

Per andarlo ad eseguire, apriamo il prompt dei comandi e spostiamoci nella directory dove abbiamo estratto il nostro file, nel mio caso nella directory: 

    alessandro@MBPdiAlessandro ~ % cd Downloads/crc-macos-1.8.0-amd64/ 
    alessandro@MBPdiAlessandro crc-macos-1.8.0-amd64 % pwd 
    Users/alessandro/Downloads/crc-macos-1.8.0-amd64

**ATTENZIONE!** 
Potrebbe essere necessario autorizzare l'secuzione del programma **crc**, che sebbene sia affidabile, potrebbe essere bloccato.

Per fare ciò, è sufficiente andare nelle impostazioni, nella sezione Sicurezza e Privacy, e cliccare su "Consenti" nel prompt che viene proposto in basso a destra.


https://support.apple.com/it-ch/guide/mac-help/mh43185/mac


Una volta nella directory, potrete invocare il comando 'setup' dell'utility crc per installare la nostra VM:

    alessandro@MBPdiAlessandro crc-macos-1.8.0-amd64 % ./crc setup
    INFO Checking if oc binary is cached              
    INFO Caching oc binary                            
    INFO Checking if podman remote binary is cached   
    INFO Caching podman remote binary                 
    INFO Checking if CRC bundle is cached in '$HOME/.crc' 
    INFO Unpacking bundle from the CRC binary         
    INFO Checking if running as non-root              
    INFO Checking if HyperKit is installed            
    INFO Setting up virtualization with HyperKit      
    INFO Will use root access: change ownership of /Users/alessandro/.crc/bin/hyperkit 
    Password:
    INFO Will use root access: set suid for /Users/alessandro/.crc/bin/hyperkit 
    INFO Checking if crc-driver-hyperkit is installed 
    INFO Installing crc-machine-hyperkit              
    INFO Will use root access: change ownership of /Users/alessandro/.crc/bin/crc-driver-hyperkit 
    INFO Will use root access: set suid for /Users/alessandro/.crc/bin/crc-driver-hyperkit 
    INFO Checking file permissions for /etc/resolver/testing 
    INFO Setting file permissions for /etc/resolver/testing 
    INFO Will use root access: create dir /etc/resolver 
    INFO Will use root access: create file /etc/resolver/testing 
    INFO Will use root access: change ownership of /etc/resolver/testing 
    INFO Checking file permissions for /etc/hosts     
    INFO Setting file permissions for /etc/hosts      
    INFO Will use root access: change ownership of /etc/hosts

Una volta terminata la fase di setup, è possibile avviare la predisposizione della macchina virtuale che servirà il nostro cluster Openshift!

    alessandro@MBPdiAlessandro crc-macos-1.8.0-amd64 % ./crc start
    INFO Checking if oc binary is cached              
    INFO Checking if podman remote binary is cached   
    INFO Checking if running as non-root              
    INFO Checking if HyperKit is installed            
    INFO Checking if crc-driver-hyperkit is installed 
    INFO Checking file permissions for /etc/resolver/testing 
    INFO Checking file permissions for /etc/hosts     
    ? Image pull secret [? for help]

A questo punto, l'installer ci sta chiedendo di inserire una chiave (Pull Secret) che occorre inserire per il download delle immagini necessarie.

Il resto del processo è qualcosa di simile, al termine dell'installazione viene generata una password per l'utente developer (pass: developer) e l'utente amministratore **kubeadmin** che dovrete salvare per poter accedere al vostro cluster!

    INFO Checking size of the disk image /Users/alessandro/.crc/cache/crc_hyperkit_4.3.8/crc.qcow2 ... 
    INFO Creating CodeReady Containers VM for OpenShift 4.3.8... 
    INFO Verifying validity of the cluster certificates ... 
    INFO Restarting the host network                  
    INFO Check internal and public DNS query ...      
    INFO Check DNS query from host ...                
    INFO Copying kubeconfig file to instance dir ...  
    INFO Adding user's pull secret ...                
    INFO Updating cluster ID ...                      
    INFO Starting OpenShift cluster ... [waiting 3m]  
    INFO                                              
    INFO To access the cluster, first set up your environment by following 'crc oc-env' instructions 
    INFO Then you can access it by running 'oc login -u developer -p developer https://api.crc.testing:6443' 
    INFO To login as an admin, run 'oc login -u kubeadmin -p kKdPx-pjmWe-b3kuu-jeZm3 https://api.crc.testing:6443' 
    INFO                                              
    INFO You can now run 'crc console' and use these credentials to access the OpenShift web console 
    Started the OpenShift cluster
    WARN The cluster might report a degraded or error state. This is expected since several operators have been disabled to lower the resource usage. For more information, please consult the documentation 


# Accesso ad Openshift

## Console Web

Al termine del setup, appuntatevi la password che viene generata, relativa all'utente "**kubeadmin**", che vi servirà per eseguire il login come amministratore. 
In alternativa, potrete usare l'utente **developer**, con password **developer**, che corrisponde ad una utenza con privilegi limitati.

Il login sarà possibile sia tramite console web, che tramite command line!

Per accedere tramite console web, sarà sufficiente utilizzare il comando.

`crc console`

Questo aprirà il browser puntando all'indirizzo generato per la console web di Openshift. Potrete accedere con l'utente '**developer**' e la password generata.

E' importante, se utilizzate l'utente developer, selezionare il provider "htpasswd_provider" nella schermata che vi verrà proposta, dopo aver accettato i certificati.
![](images/htpasswd.png)

Una volta eseguito il login, questa sarà la schermata che vi comparirà, e siete pronti a lavorare!

![](images/dashboard.png)


## Command line

In alternativa, potrete utilizzare l'utility '**oc**' per accedere ad Openshift da linea di comando.

Innanzitutto, utilizzate CRC per fare in modo che registri l'utility 'oc' nel vostro path di esecuzione:

`crc oc-env`

Una volta eseguito, potrete effettuare il login via command-line utilizzando il comando:

`oc login -u developer https://api.crc.testing:6443`

Inserendo la password, **developer**, generata in fase di start!

    [alex@pollos crc-linux-1.8.0-amd64]$ oc login -u developer https://api.crc.testing:6443
    The server uses a certificate signed by an unknown authority.
    You can bypass the certificate check, but any data you send to the server could be intercepted by others.
    Use insecure connections? (y/n): y
    
    Authentication required for https://api.crc.testing:6443 (openshift)
    Username: developer
    Password: 
    Login successful.
    
    You don't have any projects. You can try to create a new project, by running
    
        oc new-project <projectname>

Ora siete pronti ad utilizzare un cluster all-in-one funzionante al 100%!
