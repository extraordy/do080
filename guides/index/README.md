# Cap.1 - Overview of Container Technology

-   Overview della differenza tra container e VM
    
-   Enfatizzare i problemi attuali in fase ad esempio di sviluppo, librerie condivise, diverse versioni di application server, diversi runtime.
    
-   Enfatizzare i problemi che si vanno a risolvere con un approccio a container (librerie condivise, footprint di risorse, segregazione)
    
-   Enfatizzare come sia possibile portare in maniera semplice da un ambiente all’altro un’applicazione containerizzata, grazie al disaccoppiamento con l’host.
    
-   Differenze tra approccio tradizionale e approccio container
    

# Cap.2 - Overview of Container Architecture

-   Descrizione dei container, con un accenno alla gestione in kernel space dei namespace, cgroups, SECCOMP, SELinux.
    
-   Legenda dei termini utilizzati, container, immagini, repository

-   Cenni su Red Hat Container Catalog, Quay, Docker Hub

-   Introduzione a Podman, OCI, differenze con Docker
    
-   Descrizione dell'interazione di Podman con i registry, immagini e containers
    
    
# Cap.3 - Overview of Kubernetes and Openshift

-   I limiti della gestione manuale dei containers
    
-   Perchè è necessario un orchestratore
    
-   Limiti delle risorse, autoscaling in base al traffico
    
-   Reagire tempestivamente in caso di errori (health checks)
    
-   Descrizione delle strategie di deploy (Blu/Green deployment, Rolling Update, scenari per A/B testing)
    
-   Kubernetes (Orchestration, Scheduling & Isolation)
    
-   Accenno agli Operators
    
-   Openshift
    

# Cap.4 - Provisioning a Containerized Database Server

-   Gestione delle immagini con podman (search, pull)
    
-   Sintassi del nome delle immagini
    
-   Podman run, Entrypoint, ed opzioni di esecuzione (-d, -it, -e)
    
-   Dimostrazione di una messa in opera di un mysql containerizzato (exec -it)
    
-   Visualizzazione e gestione di immagini e container già presenti
    

# Cap.5 - Building Custom Container Images with Dockerfiles

-   Breve introduzione ai Dockerfile

-   Le direttive più utilizzate
    
-   La differenza tra COPY e ADD
    
-   La differenza tra CMD e ENTRYPOINT
    
-   Layers
    
-   Podman build
    
-   Dimostrazione creazione Dockerfile
    
-   Abilitare il port-forwarding in fase di esecuzione di un container
    

# Cap.6 - Creating Basic Kubernetes and Openshift Resources

-   Introduzione ai Pod
    
-   Nodi master, worker, infra
    
-   Services, PersistentVolume, PersistentVolumeClaim, ConfigMaps, Secrets.
    
-   Openshift resources (DeploymentConfig, BuildConfig, Routes)
    
-   CoreOS
    
-   Operators
    
-   Openshift CLI - oc
    
-   Descrizione dei comandi più utilizzati (New-app, get, describe, delete, exec, export, create, edit...)
    
-   Dimostrazione di creazione project e applicazione da command line
    
# Cap.7 - Creating Applications with the Source-to-Image Facility

  
-   Spiegazione del processo S2I
    
-   Benefit: Velocità di compilazione, efficienza in termini di utilizzo delle risorse, possibilità di integrare pipeline di CI/CD e patching delle applicazioni
    
-   Image Streams, breve accenno a come gestire aggiornamenti delle applicazioni a partire dall’aggiornamento di una immagine monitorata dall'ImageStream
    
-   BuildConfig VS DeploymentConfig - Rollout automatici, build automatiche grazie ai trigger
    
-   Dimostrazione S2I con:
    
    -   Applicazione buildata da codice
        
    -   Esposizione service + route
        
    -   Modifica codice su git
        
    -   Rebuild dell'applicazione
    
# Cap.8 - Creating Routes

-   Visualizzazione configurazione delle routes
    
-   Limiti delle rotte, traffico L7 http/https/websocket
    
-   Accenno ai servizi di tipo NodePort per l’esposizione di servizi non http/https
    
-   Come esporre un servizio da linea di comando (oc expose=
    
-   URL delle rotte: come vengono create di default e come personalizzarle
    
-   La application wildcard, cos'è e perchè è importante.
    
-   Dimostrazione creazione route
    
# Cap.9 - Creating Applications with the Openshift Web Console

-   Come accedere alla web console
    
-   Funzionalità della web console
    
-   Overview delle funzioni, amministrative, di gestione e prettamente legate allo sviluppo, utilizzabili in maniera semplice ed immediata direttamente da web console. 
    
-   Creare un’applicazione da web console
