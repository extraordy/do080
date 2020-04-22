#Approccio tradizionale del deployment applicativo

In un approccio tradizionale le applicazioni vengono installate su un sistema operativo e richiedono l’utilizzo di librerie condivise e/o proprietarie. Il sistema operativo può essere installato direttamente sull’hardware o può essere installato in macchine virtuali utilizzando un hypervisor come KVM (utilizzato per esempio in Red Hat Virtualization), VMware ESX, Hyper-V o Oracle VM VirtualBox.

Grazie all’utilizzo delle virtual machines possiamo per esempio creare  diverse istanze di sistema operativi per i nostri scopi. 

Questo approccio ha sempre funzionato ma presenta anche alcuni limiti tra cui:

- Tempo di boot non immediato

Quando facciamo partire una macchina virtuale il virtualizzatore crea un’istanza emulata del bios (o uefi), viene avviato il sistema operativo e, se configurata correttamente la nostra applicazione. L’avvio di una VM richiede del tempo.

- Consumo di risorse

Per il calcolo delle risorse da riservare alla VM dobbiamo considerare anche le risorse utilizzate dal sistema operativo virtualizzato

- Problema degli aggiornamenti delle librerie condivise 

Se nella macchina virtuale sono presenti per esempio due applicazioni A e B che utilizzano una stessa libreria condivisa dobbiamo chiederci per esempio:

Se aggiornassi la libreria condivisa come richiesto dall’applicazione A, l’applicazione B funzionerebbe comunque?

- Problema isolamento delle applicazioni

Sempre in presenza di più applicazioni cosa succederebbe in caso di bug presenti nell’applicazione A? Questo bug permette la lettura dei dati dell’applicazione B?
Gestione patch di sicurezza a livello di sistema operativo virtualizzato

Come gestisco le patch di sicurezza di tutti i sistemi operativi delle VM? In caso di aggiornamento del sistema operativo introduco dei problemi alle applicazioni?


Questi sono alcuni dei problemi che i linux container risolvono.


#Utilizzo dei linux container per il deployment applicativo

I linux container sono dei processi linux in grado di accogliere le nostre applicazioni.

Essendo processi linux, non abbiamo bisogno di tutto lo stack utilizzato nelle macchine virtuali.

I processi linux container utilizzano delle features proprie del kernel linux per avere un environment isolato fra gli altri e limitato nel consumo di risorse; in oltre offrono questi vantaggi rispetto all’approccio con le VM:

- Ridotto consumo di risorse

I linux container sono processi linux: non abbiamo bisogno di un ulteriore sistema operativo.
Essendo un processo, il container viene eseguito direttamente sulla macchina host esattamente come tutti i processi.

- Maggiore velocità di start-up

Non dobbiamo aspettare, come con l’approccio a macchine virtuali, il tempo di caricamento del sistema operativo virtualizzato

- Isolamento delle applicazioni

L’applicazione A presente nel  container 1 è isolata dall’applicazione B presente nel container 2 (grazie ai linux namespaces)

- Limitazione dell’utilizzo delle risorse

In linux ogni processo può essere limitato nel consumo delle risorse. I linux container sono dei processi linux quindi possono essere limitati.


- Indipendenza dall’hardware sottostante

Le applicazioni inserite nei linux container sono indipendenti dall’hardware sottostante: se creo un container sulla mia workstation RHEL, questo container girerà su tutti i server/workstation che hanno un kernel linux.

- Nessun problema di librerie condivise

Ogni linux container avrà le librerie necessarie per far funzionare l’applicazione. Grazie all’isolamento siamo certi che un eventuale aggiornamento di una libreria presente nel container 1, non interferirà mai con le librerie presenti nel container 2
















