from multiprocessing import Process, Queue
from vision import vision_process
from brain import brain_process
from actuator import actuator_process
from web.server import web_process

def main():
    vision_queue = Queue(maxsize=10)
    motion_queue = Queue(maxsize=5)
    arm_queue = Queue(maxsize=5)
    status_queue = Queue(maxsize=10)
    control_queue = Queue(maxsize=5)

    processes = [
        Process(target=vision_process, args=(vision_queue,)),
        Process(target=brain_process, args=(vision_queue, motion_queue, arm_queue, status_queue, control_queue)),
        Process(target=actuator_process, args=(arm_queue,)),
        Process(target=web_process, args=(status_queue, control_queue)),
    ]

    for p in processes:
        p.start()
        print(f"Started process: {p.name}")

    for p in processes:
        p.join()

if __name__ == "__main__":
    main()
