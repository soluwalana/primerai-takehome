#!/bin/bash

trap "exit" INT
while true; do
    echo "Waiting on kafka"
    nc -z -w 1 kafka 9092
    if [ $? -eq 0 ]; then
        echo "Kafka's ready!"
        break
    fi
    sleep 1
done

while true; do
    echo "Waiting on es"
    nc -z -w 1 es 9200
    if [ $? -eq 0 ]; then
        echo "ES is ready!"
        break
    fi
    sleep 1
done

