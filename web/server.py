
# web/server.py
from flask import Flask, Response
import json
import time
from queue import Empty
from camera.stream import video_route

def create_app(status_queue, control_queue, frame_queue=None):
    app = Flask(__name__)
    latest_status = {"state": "INIT", "detected": False, "x": 0.0, "y": 0.0}

    # --- VIDEO ---
    if frame_queue is not None:
        video_route(app, frame_queue)

    # --- STATUS STREAM (SSE) ---
    @app.route("/stream")
    def stream():
        def event_stream():
            nonlocal latest_status

            while True:
                try:
                    while True:
                        s = status_queue.get_nowait()
                        latest_status = status_to_dict(s)
                except Empty:
                    pass

                yield f"data: {json.dumps(latest_status)}\n\n"
                time.sleep(0.1)

        return Response(event_stream(), mimetype="text/event-stream")

    # --- CONTROL ---
    @app.route("/stop")
    def stop():
        control_queue.put("STOP")
        return "OK"

    return app


def status_to_dict(status):
    if hasattr(status, "detections"):
        return {
            "state": status.state,
            "detections": status.detections,
        }

    return {
        "state": status.state,
        "detected": status.detected,
        "x": status.x,
        "y": status.y,
    }


def web_process(status_queue, control_queue, frame_queue=None):
    app = create_app(status_queue, control_queue, frame_queue)
    app.run(host="0.0.0.0", port=5000, threaded=True)
