from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import RPi.GPIO as GPIO
from picamera2 import Picamera2
import cv2
import time
import logging

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading')  # Avoid eventlet issues

# Disable Flask logging noise
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# ===================== CAMERA SETUP =====================
# libcamera-hello --list-cameras
# https://bneijt.nl/pr/resolution-scale-calculator/
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(
    main={"size": (768, 432), "format": "RGB888"}  # Lower res for speed, RGB for color
))
picam2.start()

# ===================== GPIO SETUP =====================
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

IN1, IN2, ENA = 17, 18, 27
IN3, IN4, ENB = 22, 23, 24

for pin in [IN1, IN2, IN3, IN4, ENA, ENB]:
    GPIO.setup(pin, GPIO.OUT)

pwm_a = GPIO.PWM(ENA, 1000)
pwm_b = GPIO.PWM(ENB, 1000)
pwm_a.start(0)
pwm_b.start(0)

active_keys = set()

def set_motor_speed(motor, direction, speed):
    if motor == 'left':
        GPIO.output(IN1, direction == 1)
        GPIO.output(IN2, direction == -1)
        pwm_a.ChangeDutyCycle(speed)
    else:
        GPIO.output(IN3, direction == 1)
        GPIO.output(IN4, direction == -1)
        pwm_b.ChangeDutyCycle(speed)

def update_movement():
    forward = 'w' in active_keys
    backward = 's' in active_keys
    left = 'a' in active_keys
    right = 'd' in active_keys

    left_speed = right_speed = left_dir = right_dir = 0

    if forward and not backward:
        left_dir = right_dir = 1
        left_speed = right_speed = 100
    elif backward and not forward:
        left_dir = right_dir = -1
        left_speed = right_speed = 100

    if left and not right:
        if forward or backward:
            left_speed = 30
            right_speed = 100
        else:
            left_dir = -1
            right_dir = 1
            left_speed = right_speed = 60
    elif right and not left:
        if forward or backward:
            left_speed = 100
            right_speed = 30
        else:
            left_dir = 1
            right_dir = -1
            left_speed = right_speed = 60

    set_motor_speed('left', left_dir, left_speed)
    set_motor_speed('right', right_dir, right_speed)

def stop():
    active_keys.clear()
    set_motor_speed('left', 0, 0)
    set_motor_speed('right', 0, 0)

# ===================== ROUTES =====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            frame = picam2.capture_array()
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            if not ret:
                continue
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.03)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ===================== SOCKET.IO EVENTS =====================
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    stop()

@socketio.on('keydown')
def handle_keydown(data):
    key = data.get('key')
    if key:
        active_keys.add(key.lower())
        update_movement()

@socketio.on('keyup')
def handle_keyup(data):
    key = data.get('key')
    if key:
        active_keys.discard(key.lower())
        if not active_keys:
            stop()
        else:
            update_movement()

if __name__ == '__main__':
    try:
        stop()
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        stop()
        pwm_a.stop()
        pwm_b.stop()
        GPIO.cleanup()