#!/bin/bash
#watch -n 0.5 ./listen.sh ##is the best way to run this
ls -t ~/logs/* | head -1 | xargs cat | tail -n 10
