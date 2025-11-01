#!/bin/sh

docker rm test-client

docker build -t test-client ./client
if [ $? -ne 0 ]; then
    exit 1
fi

docker run -it -p 5000:5000 --name test-client test-client
if [ $? -ne 0 ]; then
    docker rmi test-client
    exit 1
fi

exit 0
