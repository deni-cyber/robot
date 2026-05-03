from enum import Enum
from dataclasses import dataclass
import time

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
    x: float
    y: float
    timestamp: float = time.time()

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