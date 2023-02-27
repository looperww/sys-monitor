# sys-monitor
### A light-weighted system monitoring tool for Libreelec.
#### The goal is to monitor the Libreelec server status in only one clean interface without using SSH and CLI. Make the monitoring efficient and effortless.

Currently only the backend API is working. Frontend development is in progress and the index page may not working properly. Feel free to participate.

The backend API returns the information of **cpu usage**, **cpu temperature**, **memory usage**, **disk usage**, **network usage** and **docker containers status**.

### How to use:

1. Clone all the files into a folder on Libreelec.

2. Build the docker image:

`docker build -t sys-monitor .`

3. Run the docker container:

        docker run -d \
            --name sys-minitor \
            --net=host \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v /proc:/host/proc:ro \
            sys-monitor

4. Go to `http://{IP_ADRESS}:8000/status` to see the json data.

**To Do: develop a frontend page to display those json data in beautiful charts/tables and fetch the data in realtime using websocket**
