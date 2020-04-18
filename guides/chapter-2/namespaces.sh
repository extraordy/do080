echo "DO080 EXTRAORDY Chapter 2: Creating an isolated process using namespaces"
echo "The isolated process will be /bin/bash"

unshare --mount --uts --ipc --net --pid --fork --user --map-root-user /bin/bash



