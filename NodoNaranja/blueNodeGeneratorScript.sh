#!/bin/bash
for ((x=0; x<$1; x++))
do
gnome-terminal -- python3 blueNode.py $2 $3

done




