from flask import Flask, render_template, request, jsonify
from flask_sock import Sock
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash
import subprocess
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
sock = Sock(app)
auth = HTTPBasicAuth()

admin_username = os.getenv("ADMIN_USERNAME")
admin_password = os.getenv("ADMIN_PASSWORD")

users = {
    admin_username: generate_password_hash(admin_password)
}

@auth.verify_password
def verify(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

@app.route('/pm2-logs/')
@auth.login_required
def index():
    return render_template("index.html")

@app.route('/pm2-logs/apps')
@auth.login_required
def list_pm2_apps():
    try:
        output = subprocess.check_output(["pm2", "jlist"])
        apps = json.loads(output)
        app_names = [app["name"] for app in apps]
        return jsonify(app_names)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sock.route('/pm2-logs/logs')
def logs(ws):
    print("WebSocket connection established for PM2 logs.")
    app_name = ws.receive()
    if not app_name:
        ws.send("No app name received.")
        return

    log_path = os.path.expanduser(f"~/.pm2/logs/{app_name}-out.log")

    try:
        with open(log_path, 'r') as f:
            f.seek(0, os.SEEK_END)

            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.01)
                    continue

                try:
                    ws.send(line)
                except Exception:
                    break
    except FileNotFoundError:
        ws.send(f"Log file not found: {log_path}")
    except Exception as e:
        ws.send(f"Error reading log file: {e}")

# if __name__ == "__main__":
#     app.run(debug=True, host='0.0.0.0', port=5000)