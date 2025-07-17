#!/bin/bash
cd /home/ec2-user/road-damage-app
docker stop road-damage || true
docker rm road-damage || true
docker build -t road-damage .
docker run -d --name road-damage -p 8501:8501 road-damage


