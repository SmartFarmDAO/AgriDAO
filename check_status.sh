#!/bin/bash
echo "--- DOCKER PS ---" > status.txt
sudo docker ps -a >> status.txt
echo "--- NGINX LOGS ---" >> status.txt
sudo docker logs agridao-nginx --tail 50 >> status.txt 2>&1
echo "--- NETSTAT ---" >> status.txt
sudo netstat -tulpn | grep -E '80|443' >> status.txt 2>&1
