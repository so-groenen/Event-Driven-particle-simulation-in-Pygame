import pygame
import numpy as np
from pygame import Vector2
from pygame.typing import ColorLike


class BoundingBox(pygame.Rect):
    def __init__(self, 
                 screen: pygame.Surface,
                 topLeft: Vector2        = Vector2(0, 0), 
                 color: ColorLike        = "black",
                 thickness: int          = 1):
        
        self.topleftVec     = topLeft
        self.toprightVec    = Vector2(screen.get_width() - topLeft.x, 
                                      topLeft.y)
        self.bottomleftVec  = Vector2(topLeft.x, 
                                      screen.get_height() - topLeft.y)
        self.bottomrightVec = Vector2(self.toprightVec.x, self.bottomleftVec.y)
        
        width  = self.toprightVec.x   - self.topleftVec.x
        height = self.bottomleftVec.y - self.topleftVec.y
        
        super().__init__(topLeft.x, topLeft.y, width, height)
        self.color      = color
        self.screen     = screen
        self.thickness  = thickness

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self, self.thickness)
    
    def getRandVec2(self, radius: float) -> Vector2:
        x = np.random.randint(self.getLeft() + radius, self.getRight() - radius)
        y = np.random.randint(self.getTop() + radius, self.getBottom() - radius)
        return Vector2(x, y)

    def getTop(self) -> float:
        return self.top + self.thickness
    
    def getBottom(self) -> float:
        return self.bottom - self.thickness
    
    def getRight(self) -> float:
        return self.right - self.thickness
    
    def getLeft(self) -> float:
        return self.left + self.thickness
