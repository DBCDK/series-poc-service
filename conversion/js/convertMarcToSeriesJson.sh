#!/bin/bash

while getopts ":h" opt; do
  case ${opt} in
    h ) # process option h
      echo "USAGE: $0 < /path/to/input_iso_in_latin1 > /path/to/output.json" 
      echo "This script converts a danMarc2 record in ISO2709 in Latin-1 charset with series fields to a series.json output"
      echo "A log file from the conversion is saved as series-conversion.log"
      exit 1
      ;;
    \? ) echo "Usage: cmd [-h] "
      ;;
  esac
done

exec jspipetool --threads 1 --log-level trace --log-file series-conversion.log isoxml marc_to_series_json.js 
