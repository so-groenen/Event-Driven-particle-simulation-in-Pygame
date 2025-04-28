import sys
from enum import Enum


class CollisionType(Enum):
    WALL     = 0
    PARTICLE = 1

class WallSide(Enum):
    TOP    = 0
    BOTTOM = 1
    LEFT   = 2
    RIGHT  = 3

class WallCollision:    
    def __init__(self,
                 side: WallSide =  WallSide.TOP,
                 time: float    = sys.float_info.max):
        
        self.side: WallSide = side
        self.time: float    = time
        
    def set(self, side: WallSide, time: float) -> None:
        self.side = side
        self.time = time
                
    def reset(self) -> None:
        self.side = WallSide.TOP
        self.time = sys.float_info.max
        

class ParticleCollision:    
    def __init__(self, 
                 partner           = None,                
                 time: float       = sys.float_info.max):
        
        self.partner          = partner
        self.time             = time
        
    def set(self, partner, time: float) -> None:
        self.partner          = partner
        self.time             = time        

    def reset(self) -> None:
        self.partner           = None
        self.time              = sys.float_info.max