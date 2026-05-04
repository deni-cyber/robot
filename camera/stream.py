
# camera/stream.py
import cv2
from flask import Response

def mjpeg_generator(frame_queue):
    while True:
        frame = frame_queue.get()  # latest frame (BGR)

        _, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


def video_route(app, frame_queue):
    @app.route('/video')
    def video():
        return Response(
            mjpeg_generator(frame_queue),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )