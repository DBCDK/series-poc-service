#!/bin/bash 

cd iso-files
for FILE in *lin
do
    ./convertLinUtf8ToIsoLatin1.sh $FILE
done
cd ../js
for ISOFILE in ../iso-files/*iso
do
    outputfilename="../../data-files/$(basename $ISOFILE | sed -e "s/-latin1.iso/.json/")"
    echo "Converting $ISOFILE"
    echo "To $outputfilename"

    ./convertMarcToSeriesJson.sh < $ISOFILE  > $outputfilename
done
