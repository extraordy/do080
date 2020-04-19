# Cap.1 - Overview of Container Technology

-   Overview della differenza tra container e VM
    
-   Enfatizzare i problemi attuali in fase ad esempio di sviluppo, librerie condivise, diverse versioni di application server, diversi runtime.
    
-   Enfatizzare i problemi che si vanno a risolvere con un approccio a container (librerie condivise, footprint di risorse, segregazione)
    
-   Enfatizzare il fatto che è possibile portare in maniera semplice da un ambiente all’altro un’applicazione containerizzata, grazie al disaccoppiamento con l’host.
    
-   Slide con differenze tra approccio tradizionale e approccio container
    

# Cap.2 - Overview of Container Architecture

-   Descrizione dei container, con un piccolo accenno alla gestione in kernel space dei namespace, cgroups, SECCOMP, SELinux.
    
-   Legenda dei termini utilizzati, container, immagini, repository
-   Cenni su Red Hat Container Catalog, Quay, Docker Hub
-   Introduzione a Podman, OCI, differenza con docker
    
-   Enfatizzare che Podman interagisce con i registry, immagini e containers
    
    
# Cap.3 - Overview of Kubernetes and Openshift

-   Spiegare i problemi di gestione manuale dei containers
    
-   Perchè è necessario un orchestratore
    
-   Limiti delle risorse, autoscaling in base al traffico
    
-   Reagire tempestivamente in caso di errori (health checks)
    
-   Accennare a Blu/Green deployment e A/B testing
    
-   Kubernetes (Orchestration, Scheduling e Isolation)
    
-   Accenno agli Operators
    
-   Openshift
    

# Cap.4 - Provisioning a Containerized Database Server

-   Dimostrazione con podman (search, pull)
    
-   Sintassi del nome delle immagini
    
-   Podman run, Entrypoint, -d, -it, -e
    
-   Dimostrazione mysql container (exec -it)
    
-   Aggiunta una piccola parentesi per come elencare le immagini già pullate e come stoppare/rimuovere un container
    

# Cap.5 - Building Custom Container Images with Dockerfiles

  

-   Breve introduzione ai Dockerfile
    
-   Enfasi sula differenza tra COPY e ADD
    
-   CMD e ENTRYPOINT
    
-   Layers
    
-   Podman build
    
-   Dimostrazione creazione Dockerfile
    
-   Portforward
    

# Cap.6 - Creating Basic Kubernetes and Openshift Resources

  

-   Introduzione ai Pod
    
-   Nodi master, worker, infra
    
-   Services, PV, PVC,CM, Secrets,
    
-   Openshift resources (DC, BC, Routes)
    
-   CoreOS
    
-   Operators
    
-   Oc utility
    
-   New-app, get, describe, delete, exec, export, create, edit
    
-   Dimostrazione con oc (creazione project e applicazione)
    

  

# Cap.7 - Creating Applications with the Source-to-Image Facility

  

-   Spiegazione del processo S2I
    
-   Enfatizzare che i developer non devono per forza sapere come funziona openshift
    
-   Benefit: patching, speed, efficient
    
-   Image Streams, breve accenno a come gestire aggiornamenti delle app a partire dall’aggiornamento di una immagine monitorata dall ’imagestream
    
-   BuildConfig VS DeploymentConfig - Rollout automatici e trigger sulla base di rebuild del codice
    
-   Dimostrazione S2I con:
    
    -   Applicazione buildata da codice
        
    -   Esposizione service + route
        
    -   Modifica codice su git - push
        
    -   oc start-build
    

  
  

# Cap.8 - Creating Routes

  

-   Esposizione dei servizi
    
-   Visualizzazione configurazione delle routes
    
-   AGGIUNTA: Limiti delle rotte, traffico L7 http/https/websocket (SI!)
    
-   AGGIUNTA: Cenno all’esistenza di servizi NodePort per l’esposizione di servizi non http/https
    
-   oc expose
    
-   Come il nome dell’url viene creata di default e come personalizzarla con --hostname
    
-   BONUS: Spiegare perché le rotte hanno un ‘pattern’ di default .apps.dominio e dove ‘si sceglie’
    
-   Dimostrazione creazione route, evitando di usare php-helloworld
    

  
  

# Cap.9 - Creating Applications with the Openshift Web Console

  

-   Come accedere alla web console
    
-   Funzionalità della web console
    
-   Enfatizzare che gran parte dei task amministrativi e di gestione delle applicazioni possono essere eseguite da web console, senza necessariamente conoscere i comandi o saper
    
-   Creare un’applicazione da web console