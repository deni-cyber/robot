import time
# import serial

def actuator_process(motion_queue, arm_queue):
    # ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

    while True:
        if not motion_queue.empty():
            motion = motion_queue.get()
            cmd = f"MOVE,{motion.linear:.2f},{motion.angular:.2f}\n"
            print("Sending:", cmd.strip())
            # ser.write(cmd.encode())

        if not arm_queue.empty():
            arm = arm_queue.get()
            cmd = f"ARM,{arm.action}\n"
            print("Sending:", cmd.strip())
            # ser.write(cmd.encode())

        time.sleep(0.02)