#!/bin/bash
echo "Running debug script..." > debug_out.txt
hostname >> debug_out.txt
whoami >> debug_out.txt
ls -la >> debug_out.txt
echo "--- CURL localhost ---" >> debug_out.txt
curl -v http://localhost >> debug_out.txt 2>&1
echo "--- DOCKER PS ---" >> debug_out.txt
docker ps >> debug_out.txt 2>&1
echo "--- SUDO DOCKER PS ---" >> debug_out.txt
sudo docker ps >> debug_out.txt 2>&1
