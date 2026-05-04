import cv2
from flask import Response
from queue import Empty

def mjpeg_generator(frame_queue):
    """
    Yields JPEG frames from the queue for the Flask response.
    """
    while True:
        try:
            # Wait for a frame with a timeout so we don't hang 
            # if the vision process crashes
            frame = frame_queue.get(timeout=2.0)

            # Encode BGR frame to JPEG
            success, jpeg = cv2.imencode('.jpg', frame)
            if not success:
                continue

            frame_bytes = jpeg.tobytes()

            # Construct the MJPEG boundary part
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                   
        except Empty:
            # If the queue is empty for 2 seconds, the vision process might be down
            print("[STREAM] No frames received from vision process...")
            continue

def video_route(app, frame_queue):
    """
    Registers the /video route with the Flask app.
    """
    @app.route('/video')
    def video():
        # multipart/x-mixed-replace tells the browser to keep replacing 
        # the current image with the next one in the stream.
        return Response(
            mjpeg_generator(frame_queue),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )