# Immagini e Dockerfiles

Abbiamo visto finora come interagire con immagini già esistenti e disponibili sui diversi registry, ma cosa succede se volessimo iniziare a costruirne una da zero?

Le **immagini** sono il cuore del nostro container, e contengono tutto ciò che serve alla nostra applicazione per funzionare senza problemi, ma può succedere che si abbia necessità di creare una immagine personalizzata, magari per aggiungere un certificato, oppure perché è necessario portare all'interno di una immagine un file di configurazione particolare.
 

## Cosa è un Dockerfile?

Iniziamo dal principo.   
Si può pensare ad un Dockerfile come ad una ricetta necessaria per costruire un'immagine.  
Tecnicamente parlando, è un file che contiene tutte le direttive necessarie al comando '**podman build**' per costruire l'immagine da utilizzare nel vostro container, esattamente come si desidera.

Solo un rapido esempio prima di entrare nei dettagli dei possibili comandi che si possono inserire nel Dockerfile.

Il seguente snippet è un Dockerfile molto semplice e di base che permette di eseguire un'immagine linux di base e che installerà httpd, aggiungendo una pagina di benvenuto custom.

    FROM ubi8
    LABEL description="Creating a custom httpd image"
    MAINTAINER Alessandro Rossi <arossi@extraordy.com>
    RUN yum install -y httpd
    EXPOSE 80
    ENV TestVar "This is a test environment variable"
    ADD index.html /var/www/html/
    USER root
    ENTRYPOINT ["/usr/sbin/httpd"]
    CMD ["-D", "FOREGROUND"]


**Struttura di un Dockerfile**

Ora abbiamo un Dockerfile di esempio, ma vediamo nello specifico alcune delle direttive che troveremo più frequentemente.

**FROM** immagine[:tag]

L'ingrediente base della vostra immagine, immaginatelo come un impasto per pizza. È qui che inizia tutta la magia, l'immagine base, di solito immagini linux minimali con le funzioni di base per eseguire una shell e alcuni comandi, come i package manager, ecc. 
Il tag è un parametro opzionale, assumerà di default "**latest**", ma se avete bisogno di una versione specifica potete usare un tag come ad esemio "**1.1**" "**v1.1**" "**test_v1**"

**COPY** sorgente destinazione

La direttiva COPY consente all'utente di copiare una o più risorse dal filesystem locale al filesystem dell'immagine docker. 
Il percorso della sorgente **deve** essere relativo alla cartella di build.

**USER** utente

Usato per specificare un utente specifico con cui verranno eseguiti i comandi successivi all'interno del container.

**WORKDIR** path

Imposta la directory di lavoro in cui il contenitore partirà. Se non specificato attraverso path assoluti, questa sarà la directory di base dal quale verranno eseguite le istruzioni RUN, CMD, ENTRYPOINT, COPY e ADD.

**ADD** sorgente destinazione

Simile a **COPY**, ma è un po' più avanzato, in quanto permette di usare percorsi remoti (URL) come sorgente, decomprimendo gli archivi, se l'immagine lo supporta e ha i pacchetti minimali necessari.

**RUN** comando

Il comando chiave per eseguire script personalizzati, eseguire l'installazione dei pacchetti con il gestore di pacchetti immagine di base (yum, dnf, ...), eseguire comandi linux e così via.  
Poiché i comandi RUN, ADD e COPY creano un "layer" partendo dall'istantanea dell'immagine fino a quel punto, è consigliato minimizzare ed eseguire una concatenazione di comandi (utilizzando '**&**'), o la copia di intere directory invece dei singoli file, quando andiamo a creare la nostra immagine, per snellire l'immagine risultante.

**ENV** chiave=valore

Questa direttiva inizializza una variabile d'ambiente al valore indicato, e questa sarà disponibile non appena si avvia il container.  
Inoltre, le variabili d'ambiente, una volta definite, possono essere riutilizzate internamente nel Dockerfile nei comandi successivi, esattamente come una qualsiasi variabile.

**EXPOSE** porta

Con la direttiva EXPOSE si **dichiara** quali sono i porti con cui il container funzionerà.  
Attenzione, questa direttiva non espone la porta fisicamente, è puramente indicativa. Possiamo utilizzare questa informazione in fase di avvio del container, per mappare ad esempio la porta indicata su una porta dell'host mediante **port-forwarding** (opzione -p host_port:container_port in podman run) 

**ENTRYPOINT** ["command", "parameter1", ...]/**CMD** ["command", "parameter1", ... ]

Sono usati per indicare un comando/script da eseguire non appena il contenitore viene eseguito con '**podman run'**.

E' assai frequente vedere nella direttiva ENTRYPOINT il comando da eseguire e separatamente nella direttiva CMD i parametri del comando che andiamo a lanciare.
Possiamo, in fase di start del container, fare un override in un solo caso, ossia quando il comando iniziale sia definito all'interno della direttiva **CMD** semplicemente passando, come abbiamo visto, il comando che desideriamo lanciare in fase di 'run' del nostro container.

**Come creare la nostra prima immagine**

Riprendiamo un attimo il nostro Dockerfile:
    FROM ubi8
    LABEL description="Creating a custom httpd image"
    MAINTAINER Alessandro Rossi <arossi@extraordy.com>
    RUN dnf install -y httpd
    EXPOSE 80
    ENV TestVar "This is a test environment variable"
    ADD index.html /var/www/html/
    USER root
    ENTRYPOINT ["/usr/sbin/httpd"]
    CMD ["-D", "FOREGROUND"]
    
Nel Dockerfile che andremo a 'buildare' ci occuperemo quindi di:
- Utilizzare l'immagine ubi8 come base (creata da RedHat, una immagine container-ready minimale)
- Eseguire l'installazione del pacchetto httpd
- Impostare una variabile d'ambiente
- Copiare un file dalla mia directory di build nella directory apache
- Informare l'utilizzatore che il mio container esporrà la porta 80
- Richiedere di eseguire il lancio del nostro server con l'utente **root** (necessario solo perché verrà utilizzata la porta 80)
- Eseguire httpd per startare il mio webserver

La sintassi del comando '**podman build**' richiede in input un path in cui sia presente un Dockerfile (ed eventuali file da 'portare' all'interno della nostra immagine).  

E' possibile specificare diverse opzioni, ma per il momento ci limiteremo a considerare:
-  "**-t**" per 'etichettare' la nostra immagine
- "**--rm**" per rimuovere i layer intermedi necessari per la costruzione

    podman build [OPZIONI] build_path  

Riprendiamo un attimo il nostro Dockerfile, spostiamoci all'interno della direcotry 'di build' e cerchiamo di costruire la nostra immagine:

    [student@workstation do080]$ podman build -t myhttpd --rm .
    STEP 1: FROM ubi8
    STEP 2: LABEL description="Creating a custom httpd image"
    --> fe346c3473a
    STEP 3: MAINTAINER Alessandro Rossi <arossi@extraordy.com>
    --> 60c4873e96a
    STEP 4: RUN yum install -y httpd
    Updating Subscription Management repositories.
    Unable to read consumer identity
    This system is not registered to Red Hat Subscription Management. You can use subscription-manager to register.
    Red Hat Universal Base Image 8 (RPMs) - BaseOS                                                                                                                                    1.1 MB/s | 761 kB     00:00    
    Red Hat Universal Base Image 8 (RPMs) - AppStream                                                                                                                                 2.2 MB/s | 3.5 MB     00:01    
    Red Hat Universal Base Image 8 (RPMs) - CodeReady Builder                                                                                                                         7.0 kB/s | 9.1 kB     00:01    
    Dependencies resolved.
    
     Package                                          Architecture                         Version                                                                Repository                                     Size
    
    Installing:
     httpd                                            x86_64                               2.4.37-16.module+el8.1.0+4134+e6bad0ed                                 ubi-8-appstream                               1.4 M
     [...output omitted...]
    Installed:
      httpd-2.4.37-16.module+el8.1.0+4134+e6bad0ed.x86_64    apr-util-openssl-1.6.1-6.el8.x86_64                            apr-util-bdb-1.6.1-6.el8.x86_64 redhat-logos-httpd-81.1-1.el8.noarch                     
      mailcap-2.1.48-3.el8.noarch                            apr-1.6.3-9.el8.x86_64                                         apr-util-1.6.1-6.el8.x86_64     httpd-tools-2.4.37-16.module+el8.1.0+4134+e6bad0ed.x86_64
      mod_http2-1.11.3-3.module+el8.1.0+4134+e6bad0ed.x86_64 httpd-filesystem-2.4.37-16.module+el8.1.0+4134+e6bad0ed.noarch
    
    Complete!
    --> efec06d00d3
    STEP 5: EXPOSE 80
    --> f9470d111a7
    STEP 6: ENV TestVar "This is a test environment variable"
    --> 62fbc9e4d22
    STEP 7: ADD index.html /var/www/html/
    --> a7fd62c0c1f
    STEP 8: USER root
    --> 7c412781e2c
    STEP 9: ENTRYPOINT ["/usr/sbin/httpd"]
    --> cc39ae197e9
    STEP 10: CMD ["-D", "FOREGROUND"]
    STEP 11: COMMIT myhttpd
    --> fef3ef10b81
    fef3ef10b81390d4a48c68c2d1f31990911ea7e01d7099d5de73b3ef91b819e5


Abbiamo indicato **'.'** perché siamo già all'interno della nostra directory di build.

La nostra immagine è ora pronta e salvata nel nostro registry locale, insieme all'altra immagine scaricata, la base image, che è stata utilizzata per la build:

    [student@workstation do080]$ podman images
    REPOSITORY                        TAG      IMAGE ID       CREATED         SIZE
    localhost/myhttpd                 latest   fef3ef10b813   2 minutes ago   271 MB
    registry.access.redhat.com/ubi8   latest   8121a9f5303b   2 weeks ago     240 MB	

Posso ora eseguire la mia immagine in un container e testarla:

    [student@workstation do080]$ podman run --name myhttpd -p 8080:80 -d localhost/myhttpd
    c920a1bd9df0681e25139c845dc475c020bed909e3537bdc4571009f9dfb0d0b
    [student@workstation do080]$ curl localhost:8080
    This is a custom index file!

Come accennato prima, non possiamo eseguire in modalità 'one-shot' un comando, per via del comando iniziale definito all'interno della direttiva **ENTRYPOINT**,  che fa si che qualsiasi cosa andassimo ad inserire in coda al comando '**podman run**' venga interpretato come un parametro del comando principale:

    podman run -it localhost/myhttpd hostname
    Usage: /usr/sbin/httpd [-D name] [-d directory] [-f file]
                           [-C "directive"] [-c "directive"]
                           [-k start|restart|graceful|graceful-stop|stop]
                           [-v] [-V] [-h] [-l] [-L] [-t] [-T] [-S] [-X]

Non abbiamo invece problemi ad eseguire un comando all'interno del nostro container avviato:

    [student@workstation do080]$ podman exec -it myhttpd /bin/bash
    [root@c920a1bd9df0 /]# cat /etc/httpd/conf/httpd.conf
    #
    # This is the main Apache HTTP server configuration file.  It contains the
    # configuration directives that give the server its instructions.
    # See <URL:http://httpd.apache.org/docs/2.4/> for detailed information.
    # In particular, see 
    # <URL:http://httpd.apache.org/docs/2.4/mod/directives.html>
    # for a discussion of each configuration directive.
	[...output omitted...]

