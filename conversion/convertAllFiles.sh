#!/bin/bash -x

cd iso-files
for FILE in *lin
do
    ./convertLinUtf8ToIsoLatin1.sh $FILE
done
cd ../js
for ISOFILE in ../iso-files/*iso
do
    echo $ISOFILE
    echo $(basename $ISOFILE)
    outputfilename=$(basename $ISOFILE | sed -e "s/-latin1.iso/.json/")

    ./convertMarcToSeriesJson.sh < $ISOFILE  > ../../data-files/$outputfilename
done
