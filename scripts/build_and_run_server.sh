#!/bin/sh

docker rm test-server

docker build -t test-server .
if [ $? -ne 0 ]; then
   exit 1
fi

docker run -it -p 5000:5000 --name test-server test-server
if [ $? -ne 0 ]; then
    docker rmi test-server
    exit 1
fi

exit 0
