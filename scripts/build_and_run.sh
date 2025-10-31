#!/bin/sh

docker rm test

docker build -t test .
if [ $? -ne 0 ]; then
    echo 'Build failed'
    exit 1
fi

docker run -it -p 5000:5000 --name test test
if [ $? -ne 0 ]; then
    echo 'Failed to run container'
    docker rmi test
    exit 1
fi

exit 0
