#!/bin/bash

if [ $# -ne 1 ]
then
    echo ""
    echo " USAGE: $0 <LINEFORMATFILE>"
    echo ""
    echo "This script converts a marc line format file in utf8 to ISO2709 in Latin1 "
    echo "Input filename should be with extension .lin like this myfile.lin"
    echo "It saves the file as original file name with myfile-latin1.iso instead"
    exit 1

fi

INPUT=$1
OUTPUT=$(basename -s .lin $INPUT)-latin.iso

echo "File will be converted to ISO2709 in charset LATIN-1 and saved as $OUTPUT"
iconv -f UTF-8 -t LATIN1 $INPUT > tmp-latin1.lin
txt2marc tmp-latin1.lin $OUTPUT
rm tmp-latin1.lin
ls -ltr
