#!/bin/bash
#watch -n 0.5 ./listen.sh #<optionalNumberOfLogsORdefault1>  ##is the best way to run this

val1="$1"
val2="$2"

if [ -z "$1" ]
  then
  val1=1
fi

if [ -z "$2" ]
  then
  val2=3
fi

ls -t ~/logs/* | head -n $val1 | xargs tail -n $val2 
