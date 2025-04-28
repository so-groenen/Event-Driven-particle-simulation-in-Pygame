from __future__ import annotations
import numpy as np
import pygame
from pygame import Vector2
from pygame.typing import ColorLike
from collisionModules import WallSide, CollisionType, ParticleCollision, WallCollision
from boundingBox import BoundingBox


class Particle:
    def __init__(self,
                 position: Vector2,
                 velocity: Vector2,
                 color: ColorLike   = "red",
                 radius: float      = 20.0,
                 mass: float        = 1):
        
        self.position = position
        self.velocity = velocity
        self.radius   = radius
        self.color    = color

        self.lastCollisionTime = 0
        self.mass              = mass
        self.collisionType     = CollisionType.WALL
        self.wallCollision     = WallCollision()
        self.particleCollision = ParticleCollision()
        
    def getCollisionTime(self) -> float:
        return min(self.wallCollision.time, self.particleCollision.time)
        
    # Overload < && > operators for priority Queue/heapq.
    def __gt__(self, other: Particle):
        return self.getCollisionTime() > other.getCollisionTime()

    def __lt__(self, other: Particle):
        return self.getCollisionTime() < other.getCollisionTime()
    
    def update(self, dt: float) -> None:
        self.position += dt*self.velocity

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, 
                           self.color,
                           self.position,
                           self.radius)
    # used for monteCarlo
    def isCollision(self, other: Particle) -> bool:
        dist    = (self.position - other.position).magnitude()
        minDist = (self.radius   + other.radius)
        return (dist <= minDist)
        
    def setLastCollisionTime(self, systemTime: float) -> None:
        self.lastCollisionTime = systemTime
        
    def setCollisionType(self) -> None:
        if self.particleCollision.time < self.wallCollision.time:
            self.collisionType = CollisionType.PARTICLE
        else:
            self.collisionType = CollisionType.WALL

    def computeBoxCollisionTime(self, box: BoundingBox, systemTime: float) -> None:
        self.wallCollision.reset()
        distance: float = 0
        colTime: float  = -1
        
        # handle up/down box collision
        if self.velocity.y < 0:
            distance = abs((self.position.y - self.radius) - box.getTop())
            colTime  = distance/abs(self.velocity.y) + systemTime
            if colTime < self.wallCollision.time:
                self.wallCollision.set(WallSide.TOP, colTime)
        elif self.velocity.y > 0:
            distance = abs((self.position.y+self.radius) - box.getBottom()) #To be checked
            colTime  = distance/abs(self.velocity.y) + systemTime
            if colTime < self.wallCollision.time:
                self.wallCollision.set(WallSide.BOTTOM, colTime)
        
        # handle left/right box collision
        if self.velocity.x > 0:
            distance = abs(box.getRight() - (self.position.x + self.radius))
            colTime  = distance/abs(self.velocity.x) + systemTime
            if colTime < self.wallCollision.time:
                self.wallCollision.set(WallSide.RIGHT, colTime)
        elif self.velocity.x < 0:
            distance = abs((self.position.x - self.radius) - box.getLeft())
            colTime  = distance/abs(self.velocity.x) + systemTime
            if colTime < self.wallCollision.time:
                self.wallCollision.set(WallSide.LEFT, colTime)

        
    def resolveBoxCollision(self, box: BoundingBox) -> None:
        match self.wallCollision.side:
            case WallSide.TOP:
                self.velocity.y *= -1
                self.position.y  = box.getTop() + self.radius 
            case WallSide.BOTTOM:
                self.velocity.y *= -1
                self.position.y  = box.getBottom() - self.radius  
            case WallSide.RIGHT:
                self.velocity.x *= -1
                self.position.x  = box.getRight() - self.radius  
            case WallSide.LEFT:
                self.velocity.x *= -1
                self.position.x  = box.getLeft() + self.radius  
        

    def getTwoParticleCollisionInfo(self, otherParticle: Particle, systemTime: float) -> ParticleCollision:
        dR: Vector2  = otherParticle.position - self.position
        dV: Vector2  = otherParticle.velocity - self.velocity
        sigma: float = otherParticle.radius   + self.radius
        b: float     = dR.dot(dV)
        
        Discriminant = b**2 - (dV.magnitude_squared())*(dR.magnitude_squared() - sigma**2)
        
        particleCollision = ParticleCollision()
        if b < 0 and Discriminant >= 0:    
            t_col    =  (-b - np.sqrt(Discriminant))/(dV.magnitude_squared())
            particleCollision.set(otherParticle, t_col + systemTime)
        return particleCollision
    
    def computeParticleCollisionTime(self, particles: list, systemTime: float) -> None:
        self.particleCollision.reset()
        for p in particles:
            if p is not self:
                newCollision = self.getTwoParticleCollisionInfo(p, systemTime)
                if newCollision.time < self.particleCollision.time:
                    self.particleCollision = newCollision
        
    def getCollisionPartner(self) -> Particle:
        return self.particleCollision.partner  
                
    def isParticleCollisionValid(self) -> bool:
        return self.lastCollisionTime >= self.particleCollision.partner.lastCollisionTime
            
    def resolveParticleCollision(self) -> None:
        partnerParticle = self.getCollisionPartner()
        
        dR: Vector2  = partnerParticle.position - self.position
        dV: Vector2  = partnerParticle.velocity - self.velocity
        sigma: float = dR.magnitude() #partnerParticle.radius + self.radius # 
        b: float     = dR.dot(dV)
   
        dV_self  = + 2*(partnerParticle.mass/(self.mass + partnerParticle.mass)) * (b/(sigma))*dR.normalize()
        dV_other = - 2*(self.mass         /(self.mass   + partnerParticle.mass)) * (b/(sigma))*dR.normalize()
        self.velocity            += dV_self
        partnerParticle.velocity += dV_other
    
    @classmethod
    def getRandVelocity(cls, low: float, high: float) -> Vector2:
        x = np.random.randint(low, high)
        y = np.random.randint(low, high)
        return Vector2(x, y)

    @classmethod
    def isCollisionWithList(cls, particle: Particle, particleList: list[Particle]):
        isCollision: bool = False
        for p in particleList:
            isCollision = particle.isCollision(p)
            if isCollision:
                break
        return isCollision
    
    @classmethod
    def MonteCarloSortInBox(cls, ParticleList: list[Particle], box: BoundingBox):
        myList = []
        for p in ParticleList:
            p.position = box.getRandVec2(p.radius)
            while cls.isCollisionWithList(p, myList):
                p.position = box.getRandVec2(p.radius)
            myList.append(p)
            
        ParticleList = myList