import psutil
from flask import Flask, jsonify
import subprocess


app = Flask(__name__)

@app.route('/cpu')
def cpu_usage():
    usage_percent = psutil.cpu_percent()
    return jsonify(usage_percent=usage_percent)

@app.route('/cpu_temp')
def cpu_temperature():
    try:
        temperature = psutil.sensors_temperatures()['coretemp'][0].current
    except KeyError:
        temperature = 'N/A'
    return jsonify(temperature=temperature)

@app.route('/gpu')
def gpu_usage():
    gpu = psutil.virtual_memory()
    return jsonify(gpu_usage=gpu.percent)

@app.route('/memory')
def memory_usage():
    memory = psutil.virtual_memory()
    return jsonify(memory_usage=memory.percent)

@app.route('/disk')
def disk_usage():
    disk = psutil.disk_usage('/')
    return jsonify(disk_usage=disk.percent)

@app.route('/network')
def network_usage():
    network = psutil.net_io_counters()
    return jsonify(bytes_sent=network.bytes_sent, bytes_recv=network.bytes_recv)

@app.route('/docker')
def docker_status():
    try:
        output = subprocess.check_output(['docker', 'ps']).decode('utf-8')
        return jsonify(docker_ps=output.strip())
    except Exception as e:
        return jsonify(error=str(e))

if __name__ == '__main__':
    app.run(debug=True, port=8000)
