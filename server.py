import psutil
from flask import Flask, jsonify, render_template
import subprocess
import time
import re
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, headers=['Content-Type', 'Access-Control-Allow-Origin'])

# CPU temperature monitoring function
def get_cpu_temp():
    #for Linux
    try:
        temps = psutil.sensors_temperatures()
        if "coretemp" in temps:
            temp = temps["coretemp"][0].current
            return temp
        elif "cpu_thermal" in temps:
            temp = temps["cpu_thermal"][0].current
            return temp
        else:
            return None
    except Exception:
        pass

    #for Mac
    try:
        temp = subprocess.check_output(['osx-cpu-temp']).decode("utf-8")
        temp = float(temp.strip().replace("°C", ""))
        return temp
    except Exception:
        return None

# Get docker info
def docker_status():
    try:
        # Get output from `docker ps` command
        output = subprocess.check_output(['docker', 'ps']).decode('utf-8')

        # Parse output to extract container information
        lines = output.strip().split('\n')[1:]
        containers = []
        for line in lines:
            fields = re.split(r'\s{2,}', line)
            container = {
                'name': fields[-1],
                'status': fields[4],
                'image': fields[1],
            }
            containers.append(container)

        return containers
    except Exception as e:
        return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/status')
def cpu():
    # Get overall CPU usage percentage
    usage_percent = psutil.cpu_percent()
    # Get CPU usage percentage for each core
    usage_percent_per_cpu = psutil.cpu_percent(percpu=True)
    # CPU clock
    try:
        freq = psutil.cpu_freq()
        cpu_clock = round(freq.current / 1000, 2)
    except Exception:
        cpu_clock = "CPU clock speed not available."

    # Get memory data
    mem = psutil.virtual_memory()
    mem_total_gb = round(mem.total / (1024 ** 3), 2)
    mem_used_gb = round(mem.used / (1024 ** 3), 2)
    percent_mem = mem.percent

    # Get temperature
    temp = get_cpu_temp()
    if temp is not None:
        temp = round(temp, 1)
    else:
        temp = 'error: CPU temperature not available.'

    # Get disk data
    disk = psutil.disk_usage('/')
    disk_total_gb = round(disk.total / (1024 ** 3), 2)
    disk_used_gb = round(disk.used / (1024 ** 3), 2)
    disk_free_gb = round(disk.free / (1024 ** 3), 2)
    percent_disk = disk.percent

    # Get network data
    network = psutil.net_io_counters()
    sent1 = network.bytes_sent
    recv1 = network.bytes_recv

    time.sleep(1)

    network = psutil.net_io_counters()
    sent2 = network.bytes_sent
    recv2 = network.bytes_recv

    bytes_sent_rate = sent2 - sent1
    bytes_recv_rate = recv2 - recv1

    bytes_sent = round(sent2 / (1024 * 1024), 2)
    bytes_recv = round(recv2 / (1024 * 1024), 2)

    # Get docker info
    containers = docker_status()
    if containers is not None:
        pass
    else:
        containers = {"error":"something wrong"}



    # Return a JSON response containing
    return jsonify({
        "cpu_usage":{
            "usage_percent_overall": usage_percent,
            "usage_percent_per_cpu": usage_percent_per_cpu,
            "clock_speed": f"{cpu_clock} GHz"},
        "memory":{
            "total_memory": mem_total_gb,
            "used_memory": mem_used_gb,
            "percent_memory": percent_mem},
        "cpu_temp":{
            'temperature': temp
        },
        "disk":{
            "total_disk": disk_total_gb,
            "used_disk": disk_used_gb,
            "percent_disk": percent_disk,
            "free_disk": disk_free_gb
        },
        "network":{
            "Send rate": round(bytes_sent_rate / 1_000_000, 2), #MB/s
            "Receive rate": round(bytes_recv_rate / 1_000_000, 2), #MB/s
            "Date sent": bytes_sent, #MB
            "Data received": bytes_recv #MB
        },
        "docker":
            containers

    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
