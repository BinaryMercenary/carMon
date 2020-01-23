#!/bin/bash
#watch -n 0.5 ./listen.sh #<optionalNumberOfLogsORdefault1>  ##is the best way to run this
val1="$1"
if [ -z "$1" ]
  then
  val1=1
fi
ls -t ~/logs/* | head -n $val1 | xargs tail -n 3 
