

# Creare applicazioni con la feature Source-to-image (S2I)

Tra le tante innovazioni che Openshift ha portato con sé dalla sua implementazione, un grande rilievo è da attribuire alla feature S2I, Source-to-image.  
Grazie al source-to-image viene data la possibilità anche ad utenti che non siano prettamente orientati al mondo operations, di mettere in opera le proprie applicazioni in maniera semplice ed efficace.
Andiamo a vedere nello specifico di cosa stiamo parlando!

## Il processo S2I

Il concetto alla base del processo **S2I** è semplice ma allo stesso tempo nasconde un meccanismo molto elaborato.

Immagine processo


Come possiamo vedere, la funzionalità di per sé ci permette, a partire da una base di codice, reperita da un repository Git ad esempio, di poter andare a buildare e successivamente deployare in modo semplice ed immediato, la nostra applicazione, rendendola di fatto immediatamente fruibile.

Detto così, sembrerebbe che stiamo parlando di qualcosa di magico, ma andiamo ad approfondire cosa sta avvenendo, nel dettaglio.

Il comando "**oc new-app**" ci permette di andare a definire una nuova applicazione all'interno del nostro namespace/progetto.  
Dietro questa semplice direttiva, in realtà c'è un mondo assai più complesso. Il comando oc new-app, infatti, non accetta in pasto un qualsiasi input, ma si aspetta di avere:
- Un Dockerfile
- Un repository Git 
- Il nome di una immagine
- Le coordinate di una immagine in particolare, nel formato visto in precedenza "registry/utente/nomeimmagine"
- *La combinazione "imageStream~repositroryGit*

Sull'ultima casistica ci soffermeremo tra un attimo, andiamo intanto a capire perché ciò è necessario.
  
E' molto semplice, a seconda dell'input che viene fornito alla direttiva "**oc new-app**" abbiamo infatti diversi comportamenti.  

-  In caso di presenza di un Dockerfile in input, Openshift si farà carico della build dell'immagine e del suo successivo deploy.
- In caso di riconoscimento di un pattern riconducibile ad una container image, si farà carico di eseguirla all'interno di un **Pod**
- In caso di presenza di un repository Git, Openshift clonerà tale repository e cercherà di reperire all'interno del contenuto, indicazioni su come poter trattare ciò che vi è al suo interno. Questo vuol dire che se il contenuto del repository rientra tra le casistiche contemplate, ad esempio un pom.xml, un sorgente Go, un sorgente .Net, Openshift riconoscerà tali formati ed istanzierà una **immagine di build**, con cui andra a compilare il nostro codice.
- Nel caso in cui avessimo un codice sorgente che ha bisogno di essere, ad esempio, compilato con una specifica versione di un particolare linguaggio, o richiedesse una particolare versione di una immagine container con cui essere eseguita, possiamo andare ad indicare quello che viene definito **ImageStream**, una risorsa Openshift, attraverso la quale andiamo a compilare/buildare la nostra immagine che verrà utilizzata all'interno dei pod.

## Benvenuto, ImageStream!

Gli imagestream (is), sono una risorsa Openshift essenziale, ma allo stesso tempo molto difficile da definire in maniera esatta.  
A me piace definirli come una sorta di semplificatore, attraverso il quale possiamo andare a mappare immagini, o particolari tag di immagini, in maniera semplice.   
Prendiamo in esempio il caso delle immagini **php**.  Bene le immagini PHP, a seconda dell versione, hanno/non hanno particolari feature, e tali feature influenzano in maniera pesante (funziona/non funziona) il nostro codice.  
Esistono tra l'altro numerose immagini php, in diversi registry, ma mettiamo che noi riteniamo valide solamente quelle provenienti dal registry **Red Hat**.  
Come possiamo fare in modo di rendere disponibili, all'interno della nostra piattaforma, le immagini php Red Hat, in modo che io sia sempre sicuro che qualsiasi sviluppatore vada a richiedere una versione specifica di PHP riceva sempre il meglio?   
Ecco che ci vengono in soccorso gli Image Stream.   
Con gli ImageStream, infatti possiamo andare a creare una referenza, ad esempio '**php**' , ed andare ad associargli diversi 'tag', detti ImageStreamTag, che in realtà puntano a versioni ben definite di immagini che abbiamo definito noi.   
Per php, Red Hat ci ha semplificato la vita, ed ha creato per noi un imageStream php, al cui interno troviamo:

    [student@workstation ~]$ oc describe imagestream php -n openshift
    Name:			php
    Namespace:		openshift
    Created:		37 hours ago
    Labels:			samples.operator.openshift.io/managed=true
    Annotations:		openshift.io/display-name=PHP
    			openshift.io/image.dockerRepositoryCheck=2020-04-22T08:43:23Z
    			samples.operator.openshift.io/version=4.3.13
    Image Repository:	image-registry.openshift-image-registry.svc:5000/openshift/php
    Image Lookup:		local=false
    Unique Images:		3
    Tags:			4
    
    7.2 (latest)
      tagged from registry.redhat.io/rhscl/php-72-rhel7:latest
        prefer registry pullthrough when referencing this tag
    
      Build and run PHP 7.2 applications on RHEL 7. For more information about using this builder image, including OpenShift considerations, see https://github.com/sclorg/s2i-php-container/blob/master/7.2/README.md.
      Tags: builder, php
      Supports: php:7.2, php
      Example Repo: https://github.com/sclorg/cakephp-ex.git
    
      * registry.redhat.io/rhscl/php-72-rhel7@sha256:e55de5852d6003ed94ea46e430a2d96ee7af936999c446f8d5abdb83005f766c
          37 hours ago
    
    7.1
      tagged from registry.redhat.io/rhscl/php-71-rhel7:latest
        prefer registry pullthrough when referencing this tag
    
      Build and run PHP 7.1 applications on RHEL 7. For more information about using this builder image, including OpenShift considerations, see https://github.com/sclorg/s2i-php-container/blob/master/7.1/README.md.
      Tags: builder, php
      Supports: php:7.1, php
      Example Repo: https://github.com/sclorg/cakephp-ex.git
    
      * registry.redhat.io/rhscl/php-71-rhel7@sha256:289ef5852151a1a3ea4fdf2581a86a60ada0719e54a5ddd78f5252742e6d2b8d
          37 hours ago
    
    7.0
      tagged from registry.redhat.io/rhscl/php-70-rhel7:latest
        prefer registry pullthrough when referencing this tag
    
      Build and run PHP 7.0 applications on RHEL 7. For more information about using this builder image, including OpenShift considerations, see https://github.com/sclorg/s2i-php-container/blob/master/7.0/README.md.
      Tags: builder, php
      Supports: php:7.0, php
      Example Repo: https://github.com/sclorg/cakephp-ex.git
    
      * registry.redhat.io/rhscl/php-70-rhel7@sha256:5fe71824f8cd33e087a8345dae0d50d246d3032b179ccfbc21a2d2aaea24e2dc
          37 hours ago


Cosa vuol dire quello che abbiamo appena visto?  
E' molto semplice, Openshift ci permette, referenziando ad esempio php:7.1 con l'opzione '**-i**' di **oc new-app**, di andare a referenziare l'immagine **registry.redhat.io/rhscl/php-71-rhel7:latest** che per noi è stata 'taggata' come php:7.1 all'interno del registry Openshift.

Tornando all'esempio che abbiamo lasciato in sospeso, se ad esempio volessimo buildare il nostro codice presente nel repository Git https://github.com/test/codiceditest.git esattamente con la versione 7.1 di PHP dell'immagine Red Hat, potremmo semplicemente indicarlo all'interno del comando **oc new-app**!

    oc new-app --name test-php -i php:7.1 https://github.com/test/codiceditest.git

O in alternativa, in maniera del tutto equivalente:

    oc new-app --name test-php php:7.1~https://github.com/test/codiceditest.git   

Con questa direttiva stiamo proprio dicendo ad Openshift di:
- Puntare all'**imageStream** php ed il relativo **tag** 7.1
- Reperire l'immagine puntata dall'**imageStreamTag** referenziato
- Utilizzare l'immagine reperita dall'**imageStreamTag** per buildare la il nostro codice

Ovviamente gli imageStream ed i relativi imagestreamtag possono essere creati in maniera custom dall'utente, per definire in maniera esatta e persistente all'interno della nostra piattaforma una immagine particolare da utilizzare come base per il deploy della nostra applicazione.    

Una caratteristica molto utile degli **imageStream** è che sono risorse monitorate, ossia un cambiamento al loro interno può dare vita ad azioni all'interno della piattaforma.  

Nello specifico, ad esempio l'aggiornamento di una immagine di build puntata dal nostro imagestreamtag, può portare ad una nuova build di eventuali applicazioni compilate con quella immagine.  
Analogamente, l'aggiornamento diretto di una immagine da cui ad esempio dipende una nostra applicazione o magari l'immagine stessa della nostra applicazione, può dare vita ad un re-deploy aggiornato della nostra applicazione, se nelle **DeploymentConfig** è specificato il trigger ImageChange, che vedremo tra poco.  


## Vantaggi del S2I
E' inutile dire che utilizzare il source-to-image per costruire le nostre applicazioni rappresenta un boost non indifferente.  
- Possiamo usufruire infatti di immagini testate e certificate per andare a buildare le nostre applicazioni, siano essi frammenti di codice inseriti in un repository Git o una intera codebase.  
- Non dobbiamo preoccuparci di specificare cosa stiamo andando a buildare, si occuperà Openshift di scegliere l'immagine più adatta a noi, e nel caso in cui sia possibile utilizzare più di una immagine, ad esempio repository Git con codice misto e non ben organizzato, ci indicherà il risultato della sua scansione, suggerendoci le diverse possibilità.
- Grande spazio per la customizzazione del processo di build. E' infatti possibile eseguire un override o andare ad integrare le routine utilizzate dal processo di source-to-image, per andare ad esempio ad inserire file particolari all'interno dell'immagine finale, eseguire azioni particolari prima, durante e dopo la build (utilizzando i build-hook), ecc.

## DeploymentConfig
Le **deploymentConfig (dc)** sono delle risorse Openshift con le quali si vanno a definire nel dettaglio i contenuti di un particolare deploy, come ad esempio:
- Immagine da utilizzare ed eseguire nel pod
- Numero di repliche desiderate
- Porte esposte
- Eventuali volumi di persistenza
- Eventuali variabili d'ambiente da impostare

Quello che rende uniche le deploymentConfig, sono alcune caratteristiche, non presenti ad esempio nei Deployment:
- Salvataggio dello stato ad ogni deploy, per permettere il **rollback** automatico dell'applicazione ad esempio ad una versione precedente.
- Trigger per l'esecuzione di un re-deploy a seguito di una particolare condizione.
- Implementazione di **lifecycle hooks** per i pod, per definire un comportamento particolare in un determinato stato del ciclo di vita di un pod.

Un esempio di deploymentconfig è:

    [student@workstation ~]$ oc describe deploymentconfig hello-extraordy
    Name:		hello-extraordy
    Namespace:	hello-extraordy
    Created:	24 hours ago
    Labels:		app=hello-extraordy
    Annotations:	openshift.io/generated-by=OpenShiftNewApp
    Latest Version:	3
    Selector:	app=hello-extraordy,deploymentconfig=hello-extraordy
    Replicas:	1
    Triggers:	Config, Image(hello-extraordy@latest, auto=true)
    Strategy:	Rolling
    Template:
    Pod Template:
      Labels:	app=hello-extraordy
    		deploymentconfig=hello-extraordy
      Annotations:	openshift.io/generated-by: OpenShiftNewApp
      Containers:
       hello-extraordy:
        Image:		image-registry.openshift-image-registry.svc:5000/hello-extraordy/hello-extraordy@sha256:8becaf974de7b020007ad79fba9cc68067f7be60fe8035d9db1dd7b5c38db856
        Port:		<none>
        Host Port:		<none>
        Environment:	<none>
        Mounts:		<none>
      Volumes:		<none>
    
    Deployment #3 (latest):
    	Name:		hello-extraordy-3
    	Created:	13 hours ago
    	Status:		Complete
    	Replicas:	1 current / 1 desired
    	Selector:	app=hello-extraordy,deployment=hello-extraordy-3,deploymentconfig=hello-extraordy
    	Labels:		app=hello-extraordy,openshift.io/deployment-config.name=hello-extraordy
    	Pods Status:	1 Running / 0 Waiting / 0 Succeeded / 0 Failed
    Deployment #2:
    	Created:	24 hours ago
    	Status:		Complete
    	Replicas:	0 current / 0 desired
    Deployment #1:
    	Created:	24 hours ago
    	Status:		Complete
    	Replicas:	0 current / 0 desired
    
    Events:	<none>

Come possiamo vedere, abbiamo delle informazioni relative ai singoli **deploy** eseguiti per la nostra applicazione, lo stato dei nostri pod, le repliche desiderate e sopratutto quella che è la configurazione, relativa ad **Image**, **Volume**, **Port**, che andranno a definire effettivamente le caratteristiche all'interno del pod che ospiterà la nostra applicazione.  
I comandi che possiamo utilizzare per andare a 'pilotare' un deploy sono:

    oc rollout latest deploymentconfig/nomedc
Con questo comando andiamo ad eseguire il deploy dell'ultima versione della nostra applicazione, nel caso in cui non siano state eseguite modifiche rispetto alla precedente, sarà di fatto un redeploy della stessa.

    oc rollback deploymentconfig/nomedc

In questo caso andremo a rieseguire il deploy della versione immediatamente precedente della nostra applicazione.  

Inoltre, di default viene impostato un **trigger** sulla modifica della deploymentconfig, ovvero ad ogni modifica eseguita con:

    oc edit deploymentconfig/nomedc
Nel momento in cui andiamo a salvare le nostre modifiche, se vi sono cambiamenti il sistema andrà automaticamente ad allineare la piattaforma con le nuove modifiche, eseguendo un deploy dell'applicazione coerentemente con le nuove indicazioni.

## BuildConfig
Una **buildConfig (bc)** è una risorsa analoga alle deploymentConfig, con la differenza che si ocucpa di gestire e determinare quello che è il processo di build della nostra applicazione.  
Come abbiamo visto, nel caso delle **deploymentconfig**, andiamo a definire dei comportamenti e delle logiche prettamente legate alla fase di **deploy**, nel caso delle **buildconfig** andiamo a definire delle strategie di build, eventuali **hook pre-post build**, dei trigger che devono scatenare una build, ad esempio una push su un determinato repository, attraverso i ***webhook GitLab***, oppure build triggerate attraverso chiamate REST ad un **webhook generico** definito all'interno della buildconfig.  
Per avere un'idea di ciò che possiamo avere all'interno di una buildConfig, andiamo a prendere come esempio quella della nostra applicazione di esempio!  

    [student@workstation ~]$ oc describe bc hello-extraordy
    Name:		hello-extraordy
    Namespace:	hello-extraord
    Created:	25 hours ago
    Labels:		app=hello-extraordy
    Annotations:	openshift.io/generated-by=OpenShiftNewApp
    Latest Version:	3
    
    Strategy:	Source
    URL:		https://github.com/kubealex/hello-go.git
    From Image:	ImageStreamTag openshift/golang:1.11.5
    Output to:	ImageStreamTag hello-extraordy:latest
    
    Build Run Policy:	Serial
    Triggered by:		Config, ImageChange
    Webhook GitHub:
    	URL:	https://api.ocp4.hetzner.lab:6443/apis/build.openshift.io/v1/namespaces/hello-extraordy/buildconfigs/hello-extraordy/webhooks/<secret>/github
    Webhook Generic:
    	URL:		https://api.ocp4.hetzner.lab:6443/apis/build.openshift.io/v1/namespaces/hello-extraordy/buildconfigs/hello-extraordy/webhooks/<secret>/generic
    	AllowEnv:	false
    Builds History Limit:
    	Successful:	5
    	Failed:		5
    
    Build			Status		Duration	Creation Time
    hello-extraordy-3 	complete 	1m15s 		2020-04-23 12:00:48 +0200 CEST
    hello-extraordy-2 	complete 	1m24s 		2020-04-23 00:45:14 +0200 CEST
    hello-extraordy-1 	complete 	1m26s 		2020-04-23 00:31:03 +0200 CEST
    
    Events:	<none>

Come possiamo vedere, abbiamo anche in questo caso uno storico delle build precedenti, la tipologia di strategy, nel nostro caso **Source** in quanto la nostra applicazione è stata creata a partire da un codice sorgente compilato in Golang ( riportato nella sezione **From Image:	ImageStreamTag openshift/golang:1.11.5**)   

Come accennato prima, abbiamo alcuni eventi che potrebbero scaturire una nuova build automatica delle nostre applicazioni, nello specifico:
- Webhook Gitlab: endpoint creati da Openshift e che possiamo riportare nei nostri repository per notificare ad esempio ogni commit/push all'interno del nostro repository.
- Webhook generici: endpoint creati da Openshift e che poissiamo chiamare, ad esempio con curl o Postman per far triggerare una nuova build
- Il comando `oc start-build buildconfig/nomebc`
- La modifica dell'iimageStream di build nel caso in cui sia definito un **TriggeredBy** di tipo **ImageChange**
