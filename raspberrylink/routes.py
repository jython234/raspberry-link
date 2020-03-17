from flask import jsonify
from raspberrylink import app, software_name, software_version, obdmanager, server_config, util

api_version_major = 2
api_version_minor = 1


@app.route('/apiver')
def apiver():
    return jsonify({
        "major": api_version_major,
        "minor": api_version_minor
    })


@app.route('/feature_request')
def feature_request():
    audio_running = util.check_audio_running()
    obj = {
        "vehicle": "Unknown",
        "server": software_name,
        "version": software_version,
        "audio": audio_running and server_config['audio'].getboolean("enabled"),
        "handsfree": audio_running and server_config['audio'].getboolean("handsfree-enabled"),
        "camera": server_config['camera'].getboolean("enabled"),
        "obd": server_config['obd'].getboolean("enabled")
    }
    return jsonify(obj)
