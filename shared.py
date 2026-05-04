from enum import Enum
from dataclasses import dataclass
import time

MODELPATH="/home/deni/Music/Desktop/robot/models/litter-detection-linux-aarch64-v3-impulse-#1.eim"


class RobotState(Enum):
    IDLE = 0
    SEARCHING = 1
    TARGET_LOCKED = 2
    APPROACHING = 3
    PICKING = 4

@dataclass
class Detection:
    detected: bool
    confidence: float
    x: float   # normalized (nx)
    y: float   # normalized (ny)
    distance: float = 0.0
    timestamp: float = 0.0

@dataclass
class MotionCommand:
    linear: float   # forward/back
    angular: float  # turning

@dataclass
class ArmCommand:
    action: str  # "PICK", "REST"

@dataclass
class Status:
    state: str
    detected: bool
    x: float
    y: float