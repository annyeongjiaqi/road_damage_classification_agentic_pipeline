#!/bin/bash
set -e
cd /home/ec2-user/app
# Rebuild container
docker-compose down --remove-orphans
docker-compose up -d --build
# Notify orchestrator about success
python pipeline_orchestrator.py --deploy-event success
