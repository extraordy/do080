# Podman - Interagire con i container
Podman è un tool, ormai di base nei sistemi RHEL/Fedora/Centos più recenti, che di fatto va a sostituire il ben più conosciuto Docker, al momento non più supportato.
Tuttavia, per chi ha già avuto modo di interagire con Docker, si renderà quasi subito conto che i comandi che andremo ad utilizzare sono esattamente coerenti con quanto già utilizzato.  
Configurandosi come un sostituto a tutti gli effetti di Docker, infatti, durante lo sviluppo si è cercato di rendere il 'passaggio' il meno drastico possibile.

Le differenze principali tra Podman e Docker sono:
- L'architettura - Podman si interfaccia direttamente con:
	- Registry
	- Containers
	- Immagini 
	- Container Runtime (runc/crun)

Non è più infatti necessaria la presenza di un demone sempre attivo, che oltre a configurarsi come un possibile flaw di sicurezza di fatto è un single point of failure che rischia di rendere inutilizzabili i nostri container in caso di un problema al demone in esecuzione.
- Podman permette l'esecuzione ***rootless*** e root di container.
- Podman è compatibile con i **cgroups v2** introdotti in Fedora31

Ma veniamo a noi, e vediamo come andare ad utilizzare un container con Podman.

## Installare Podman e verificare l'installazione
Podman si configura come un pacchetto da installare, disponibile nelle maggiori distribuzioni e preinstallato, come accennato nelle recenti versioni di RHEL/Fedora/Centos.

Qualora non fosse già installato, è possibile procedere andando ad installare il pacchetto ***podman***:

    sudo dnf install podman

Una volta installato, sarà possibile verificare l'installazione e la versione ora presente:

    [student@workstation ~]$ podman --version
    podman version 1.8.2

## Ricercare una immagine all'interno dei registry
Durante l'installazione, Podman risulta preconfigurato con una serie di repository, pubblici, da cui attingerà per la ricerca di immagini ed il loro utilizzo per la creazione dei nostri container.
Per completezza, tale configurazione è possibile verificarla nel file: 

    [student@workstation ~]$ cat /etc/containers/registries.conf  |grep registries.search  -A2
    [registries.search]
    registries = ['docker.io', 'registry.fedoraproject.org', 'registry.access.redhat.com', 'registry.centos.org', 'quay.io']

Possiamo verificare facilmente, con una ricerca, che in effetti sono proprio i registry che vengono 'interrogati':

    [student@workstation ~]$ podman search nginx
    INDEX               NAME                                                                   DESCRIPTION                                       STARS   OFFICIAL   AUTOMATED
    docker.io           docker.io/library/nginx                                                Official build of Nginx.                          13006   [OK]       
    [...output omitted...]
    fedoraproject.org   registry.fedoraproject.org/f29/nginx                                                                                     0                  
    [...output omitted...]
    redhat.com          registry.access.redhat.com/rhscl/nginx-112-rhel7                       Nginx is a web server and a reverse proxy se...   0                  
    [...output omitted...]
    centos.org          registry.centos.org/bamachrn/nginx-header                                                                                0                  
    [...output omitted...]
    quay.io             quay.io/kubernetes-ingress-controller/nginx-ingress-controller         NGINX Ingress controller built around the [K...   0           

Possiamo prelevare una immagine particolare andando a specificarla nel comando '**podman pull**'.
In questo modo, l'immagine sarà prelevata e salvata all'interno della directory 

    [student@workstation ~]$ podman docker.io/library/httpd 
    Trying to pull docker.io/library/httpd...
    Getting image source signatures
    Copying blob 6faf90d050b2 done  
    Copying blob e984dd982a6e done  
    Copying blob 963280e5cf81 done  
    Copying blob 123275d6e508 done  
    Copying blob 962b56984bb0 done  
    Copying config bdc169d27d done  
    Writing manifest to image destination
    Storing signatures

I dati dell'immagine prelevata vengono salvati all'interno della directory:

    ~/.local/share/containers/

Per reperire rapidamente le informazioni relative alle immagini presenti in locale possiamo utilizzare il comando '**podman images**':

    [student@workstation do080]$ podman images
    REPOSITORY                TAG      IMAGE ID       CREATED      SIZE
    docker.io/library/httpd   latest   bdc169d27d36   2 days ago   171 MB

## Avviare un container
Come abbiamo visto, un **container** non è altro che un ecosistema isolato ritagliato dal sistema in cui risiede, al cui interno viene eseguita una **immagine**, che di fatto costituisce l'insieme di risorse (filesystem di base, applicativi, ecc.) che andranno a risiedere all'interno del nostro container.
Utilizzando il comando **podman run** andiamo proprio ad eseguire l'immagine di nostro interesse all'interno di un container, la cui creazione viene presa in carico da Podman.

Ad esempio, per andare a creare un container che ci renda disponibile un **server http** potremo semplicemente andare ad eseguire il seguente comando:

    [student@workstation ~]$ podman run -p 8080:80 httpd 
    Trying to pull docker.io/library/httpd...
    Getting image source signatures
    Copying blob 6faf90d050b2 done  
    Copying blob e984dd982a6e done  
    Copying blob 963280e5cf81 done  
    Copying blob 123275d6e508 done  
    Copying blob 962b56984bb0 done  
    Copying config bdc169d27d done  
    Writing manifest to image destination
    Storing signatures
    AH00558: httpd: Could not reliably determine the server's fully qualified domain name, using 10.0.2.100. Set the 'ServerName' directive globally to suppress this message
    AH00558: httpd: Could not reliably determine the server's fully qualified domain name, using 10.0.2.100. Set the 'ServerName' directive globally to suppress this message
    [Sat Apr 18 21:55:58.154620 2020] [mpm_event:notice] [pid 1:tid 140578934793344] AH00489: Apache/2.4.43 (Unix) configured -- resuming normal operations
    [Sat Apr 18 21:55:58.156629 2020] [core:notice] [pid 1:tid 140578934793344] AH00094: Command line: 'httpd -D FOREGROUND'

In questo caso, l'immagine è configurata in modo tale da eseguire automaticamente un processo (httpd) che rimane in attesa di connessioni, esattamente come accadrebbe normalmente. 
Inoltre, abbiamo specificato l'opzione -p 8080:80 che ci consente di eseguire un '**port forwarding**' sulla porta 8080 dell'host da cui eseguiamo il comando della porta 80 del container.
Tuttavia questo ci impedisce di fare qualsiasi altra azione, in quanto l'interruzione dell'esecuzione del comando **podman run** andrebbe di fatto a stoppare l'esecuzione del nostro container.

Per questo Podman, analogamente a Docker, ci mette a disposizione una opzione, '**-d**'  o '**--detach**' che ci permette di mandare in background l'esecuzione del nostro container:

    [alex@pollos do080]$ podman run -d -p 8080:80 httpd 
    30fa500dc20090c20d8c1307e182bbc0c2cd8cfdb9934df5a1fb5355d9778c1f
Come vedete, viene 'staccato' un identificativo, che rappresenta l'ID del container che stiamo eseguendo.

Possiamo facilmente testare la bontà dell'esecuzione, con una semplice **curl**:

    [alex@pollos do080]$ curl localhost:8080
    <html><body><h1>It works!</h1></body></html>

## Eseguire comandi all'interno di un container
Abbiamo visto che, nel nostro container di esempio, l'immagine httpd al termine del caricamento eseguiva automaticamente il suo processo.
In realtà, non tutte le immagini necessariamente 'eseguono' qualcosa al loro interno, e comunque qualsiasi sia il comando che viene eseguito, può essere sovrascritto da linea di comando.
Tornando alla nostra immagine httpd, ora il container è in esecuzione in background, ma potremmo ad esempio lanciare una nuova istanza, che semplicemente ci stampi l'hostname del container in cui andrà ad essere eseguita la nostra immagine:

    [alex@pollos do080]$ podman run httpd hostname
    5c55979cfe57

Possiamo facilmente verificare, utilizzando il comando **podman ps**, che l'unico container in esecuzione è ancora quello lanciato in precedenza, mentre il successivo 'run' ha creato un container, eliminato subito dopo la sua esecuzione:

    [student@workstation do080]$ podman ps
    CONTAINER ID  IMAGE                           COMMAND           CREATED        STATUS            PORTS                 NAMES
    30fa500dc200  docker.io/library/httpd:latest  httpd-foreground  7 minutes ago  Up 7 minutes ago  0.0.0.0:8080->80/tcp  peaceful_bardeen

Possiamo anche eseguire ad esempio dei comandi interattivi, come aprire una shell, che richiedano un input dell'utente.
Podman ci mette a disposizione le opzioni -i (interactive) e -t (tty) che permettono di intercettare l'input dell'utente ed allocano un terminale per il nostro container, in modo da poterci interagire:

    [student@workstation do080]$ podman run -it httpd /bin/bash
    root@1463d6cd2b6b:/usr/local/apache2# echo Ciao dal DO080!
    Ciao dal DO080!
    root@1463d6cd2b6b:/usr/local/apache2# exit
    exit
    [student@workstation do080]$ 

E' altresì possibile interagire con i container già in esecuzione, andando ad eseguire comandi al loro interno, utilizzando l'ID o il nome del container da passare al comando **'podman exec'**.  
Anche per questo tipo di esecuzione valgono le opzioni **-i** e **-t**, ed analogamente possiamo eseguire comandi 'oneshot' al suo interno:

    [student@workstation do080]$ podman exec 30fa500dc200 hostname
    30fa500dc200

---

    [student@workstation do080]$ podman exec -it 30fa500dc200 /bin/bash
    root@30fa500dc200:/usr/local/apache2# hostname
    30fa500dc200
    root@30fa500dc200:/usr/local/apache2# exit
    exit

Vi chiederete se è un caso che l'hostname sia proprio uguale all'ID 'abbreviato' del nostro container; no! Non è un caso  :)


## Arrestare un container e rimuoverlo
Come abbiamo visto, possiamo eseguire in background i nostri container, ma potremmo aver bisogno di bloccarne l'esecuzione, o rimuovere container che non utilizziamo più.
Per interrompere l'esecuzione di un container, possiamo utilizzare il comando '**podman stop**' specificando il nome o l'identificativo del container che desideriamo interrompere:

    [student@workstation do080]$ podman stop 30fa500dc200
    30fa500dc20090c20d8c1307e182bbc0c2cd8cfdb9934df5a1fb5355d9778c1f  

Possiamo verificare immediatamente che il nostro container non è più in esecuzione:

    [student@workstation do080]$ podman ps
    CONTAINER ID  IMAGE  COMMAND  CREATED  STATUS  PORTS  NAMES


Tuttavia, utilizzando l'opzione '-a' possiamo vedere che il container è ancora 'presente' nel nostro sistema:

    [student@workstation do080]$ podman ps -a
    CONTAINER ID  IMAGE                           COMMAND           CREATED         STATUS                     PORTS                 NAMES
    1463d6cd2b6b  docker.io/library/httpd:latest  /bin/bash         13 minutes ago  Exited (0) 12 minutes ago                        serene_wescoff
    5c55979cfe57  docker.io/library/httpd:latest  hostname          17 minutes ago  Exited (0) 17 minutes ago                        nice_brattain
    30fa500dc200  docker.io/library/httpd:latest  httpd-foreground  24 minutes ago  Exited (0) 2 minutes ago   0.0.0.0:8080->80/tcp  peaceful_bardeen
    8b5c76fcbb8e  docker.io/library/httpd:latest  httpd-foreground  25 minutes ago  Created                    0.0.0.0:80->80/tcp    boring_nightingale

Possiamo a questo punto andare a rimuovere il container appena interrotto, utilizzando il comando '**podman rm**', a cui andremo anche in questo caso a passare l'ID o il nome del container da rimuovere:

    [student@workstation do080]$ podman rm 30fa500dc20090c20d8c1307e182bbc0c2cd8cfdb9934df5a1fb5355d9778c1f
    30fa500dc20090c20d8c1307e182bbc0c2cd8cfdb9934df5a1fb5355d9778c1f

Verifichiamo a questo punto che effettivamente il container non è più presente nella lista:

    [student@workstation do080]$ podman ps -a
    CONTAINER ID  IMAGE                           COMMAND           CREATED         STATUS                     PORTS               NAMES
    1463d6cd2b6b  docker.io/library/httpd:latest  /bin/bash         14 minutes ago  Exited (0) 13 minutes ago                      serene_wescoff
    5c55979cfe57  docker.io/library/httpd:latest  hostname          18 minutes ago  Exited (0) 18 minutes ago                      nice_brattain
    8b5c76fcbb8e  docker.io/library/httpd:latest  httpd-foreground  25 minutes ago  Created                    0.0.0.0:80->80/tcp  boring_nightingale


