# Come utilizzare un cluster Openshift senza installazione
L'installazione di **Openshift 4.x** è stata di gran lunga semplificata rispetto alle versioni precedenti.  
L'utilizzo dei playbook e la configurazione di tutte le variabili della piattaforma sono stati sostituiti da un installer snello, che pevede due modalità di installazione, a seconda se l'infrastruttura venga o meno preparata dall'utente.  
Esistono infatti due metodologie:

**UPI** --> User provisioned infrastructure  
**IPI** --> Installer providioned infrastructure

Nel primo caso, sarà necessario configurare anche la parte infrastrutturale (vSphere, libvirt, bare metal), nel secondo invece, l'installer si interfaccerà con l'ecosistema sottostante (AWS, GoogleCloud, Openstack) per il provisioning dell'infrastruttura.

In entrambi i casi, tuttavia, le richieste a livello hardware sono molto esose, pertanto vogliamo suggerirvi alcuni metodi per poter avere a disposizione un piccolo cluster, che però vi permetterà di fruire al massimo del corso e dove potrete replicare ciò che vedremo insieme.

Di seguito troverete delle piccole linee guida per utilizzare i tre metodi che abbiamo scelto di proporvi:

- [Openshift Playground - Instruqt (Playground in web browser, senza registrazione)](instruqt-playground/README.md)
- [Openshift Online (Cluster Openshift minimale su infrastruttura Red Hat, con registrazione)](openshift-online/README.md)
- [CodeReady Containers - CRC (VM all-in-one con un cluster Openshift minimale)](crc/README.md)
