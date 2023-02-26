import psutil
from flask import Flask, jsonify
import subprocess
import time
import re


app = Flask(__name__)

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

@app.route('/cpu')
def cpu():
    # Get overall CPU usage percentage
    usage_percent = psutil.cpu_percent()

    # Get CPU usage percentage for each core
    usage_percent_per_cpu = psutil.cpu_percent(percpu=True)

    #CPU clock
    try:
        freq = psutil.cpu_freq()
        cpu_clock = round(freq.current / 1000, 2)
    except Exception:
        cpu_clock = "CPU clock speed not available."

    # Return a JSON response containing both values
    return jsonify({
        "usage_percent_overall": usage_percent,
        "usage_percent_per_cpu": usage_percent_per_cpu,
        "clock_speed": f"{cpu_clock} GHz"
    })

@app.route('/cpu_temp')
def cpu_temp():
    temp = get_cpu_temp()
    if temp is not None:
        return jsonify({'temperature': round(temp, 1)})
    else:
        return jsonify({'error': 'CPU temperature not available.'}), 500


@app.route('/memory')
def memory_usage():
    mem = psutil.virtual_memory()
    mem_total_gb = round(mem.total / (1024 ** 3), 2)
    mem_used_gb = round(mem.used / (1024 ** 3), 2)
    percent_mem = mem.percent
    return jsonify({
        "total_memory": mem_total_gb,
        "used_memory": mem_used_gb,
        "percent_memory": percent_mem})

@app.route('/disk')
def disk_usage():
    disk = psutil.disk_usage('/')
    disk_total_gb = round(disk.total / (1024 ** 3), 2)
    disk_used_gb = round(disk.used / (1024 ** 3), 2)
    disk_free_gb = round(disk.free / (1024 ** 3), 2)
    percent_disk = disk.percent
    return jsonify({
        "total_disk": disk_total_gb,
        "used_disk": disk_used_gb,
        "percent_disk": percent_disk,
        "free_disk": disk_free_gb
    })

@app.route('/network')
def network_usage():
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

    return jsonify({
        "Send rate": round(bytes_sent_rate / 1_000_000, 2), #MB/s
        "Receive rate": round(bytes_recv_rate / 1_000_000, 2), #MB/s
        "Date sent": bytes_sent, #MB
        "Data received": bytes_recv #MB

    })

@app.route('/docker')
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

        return jsonify(containers)
    except Exception as e:
        return jsonify(error=str(e))

if __name__ == '__main__':
    app.run(debug=True, port=8000)
