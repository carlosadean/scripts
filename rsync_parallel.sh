#/bin/bash
# SETUP OPTIONS
export SRCDIR="/mnt/transfer/tmp/Y3A1_JPG_HiPS"
export DESTDIR="/mnt/transfer/tmp/Y3A1_JPG_HiPS-old"
export THREADS="24"

# RSYNC DIRECTORY STRUCTURE
rsync -zrvP -f"+ */" -f"- *" $SRCDIR/ $DESTDIR/
# FOLLOWING MAYBE FASTER BUT NOT AS FLEXIBLE
# cd $SRCDIR; find . -type d -print0 | cpio -0pdm $DESTDIR/
# FIND ALL FILES AND PASS THEM TO MULTIPLE RSYNC PROCESSES
cd $SRCDIR; find . -type f -print0 | xargs -0 -n1 -P$THREADS -I% rsync -azvP % $DESTDIR/%
 
# IF YOU WANT TO LIMIT THE IO PRIORITY, 
# PREPEND THE FOLLOWING TO THE rsync & cd/find COMMANDS ABOVE:
#   ionice -c2
