# sys-monitor
A light weight system monitoring tool for Libreelec which let you to monitor the system status without using SSH and CLI.

The backend API returns the information of cpu usage, cpu temperature, memory usage, disk usage, network usage and docker containers status. 

Build the docker image: 
     
docker build -t sys-monitor .

Run the docker container:

docker run -d \
    --privileged \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -p 8000:8000 \
    sys-monitor

Go to http://{IP ADRESS}:8000/status to see the data.

Frontend development is in progress.
