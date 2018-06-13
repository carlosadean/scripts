#!/bin/bash

[ "$1" == "" ] && { echo "Provide the list of files to download."; exit 1; } 

file=$1
nstreams=$2

if [ ! -z "$nstreams" ]
then
        nstreams=1
    fi

nproc=0
files=$(cat $file | xargs)

for file in $files
do 
    downl="nok"
    while [ $downl != "ok" ]
    do
        if [ $nproc -lt $nstreams ]
        then
            echo "wget -c -nd -np --user=XXXX --password=XXXX $file" &
            downl="ok"
            let nproc=$(ps | grep wget | wc -l)
        else
            sleep 10
            let nproc=$(ps | grep wget | wc -l)
        fi
    done
done

wait
