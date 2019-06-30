#!/bin/bash
echo $1 #Number of blueNodes to create
echo $2 #IP of the orangeNode
echo $3 #Port of the orangeNode

for ((x=0; x<$1; x++))
do
gnome-terminal -- python3 blueNode.py $2 $3
done




