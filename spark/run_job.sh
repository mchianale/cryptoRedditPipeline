#!/bin/bash

docker exec -it spark-master /opt/bitnami/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    ./spark/job.py