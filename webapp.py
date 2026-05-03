from flask import Flask, jsonify

def create_app(status_queue, control_queue):
    app = Flask(__name__)
    latest_status = {"state": "INIT"}

    @app.route("/status")
    def status():
        nonlocal latest_status
        while not status_queue.empty():
            s = status_queue.get()
            latest_status = {
                "state": s.state,
                "detected": s.detected,
                "x": s.x,
                "y": s.y
            }
        return jsonify(latest_status)

    @app.route("/stop")
    def stop():
        control_queue.put("STOP")
        return "OK"

    return app

def web_process(status_queue, control_queue):
    app = create_app(status_queue, control_queue)
    app.run(host="0.0.0.0", port=5000)