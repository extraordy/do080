# Breve storia dei containers

L’idea di  isolare un processo è presente fin dal 1979 nel sistema operativo UNIX version 7 grazie all’adozione del chroot system. Nel corso degli anni sono state create molte soluzione per poter creare processi isolati e limitati, ma è circa nel 2008 che il linux kernel incomincia ad offrire due funzionalità fondamentali per la creazione di processi isolati e limitati: cgroups, namespaces, seccomp (introdotta nel 2014). (il mount namespaces era presente già nel 2002)



## Namespaces (dal 2002)

Grazie ai namespaces possiamo isolare un processo linux. Questa è una lista dei namespaces (presa dal man) presenti nel kernel linux:

Namespace            Isolates
Cgroup         Cgroup root directory
IPC            System V IPC, POSIX message queues
Network        Network devices, stacks, ports, etc.
Mount          Mount points
PID            Process IDs
User           User and group IDs
UTS            Hostname and NIS domain name


Se per esempio creiamo un processo isolato con il namespace ‘Network’, il suddetto processo sarà isolato a livello networking dall’host che l’ha creato.


## CGroups (dal 2007)

Grazie a Control groups (cgroups) possiamo limitare il consumo di risorse da parte di un processo


## Seccomp (dal 2014)

Seccomp ci permette di limitare l'utilizzo delle syscall da parte dei processi.


