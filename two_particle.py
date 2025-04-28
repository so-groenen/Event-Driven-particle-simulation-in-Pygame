from __future__ import annotations #For type hinting "not yet declared" classes
import sys
import pygame
import copy
from pygame import Vector2
from pygame.typing import ColorLike 
from enum import Enum
import numpy as np
import heapq


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
                 partner: Particle = None,                
                 time: float       = sys.float_info.max):
        
        self.partner          = partner
        self.time             = time
        
    def set(self, partner, time: float) -> None:
        self.partner          = partner
        self.time             = time        

    def reset(self) -> None:
        self.partner           = None
        self.time              = sys.float_info.max
        self.deltaVel_self     = None
        self.deltaVel_partner  = None

class BoundingBox(pygame.Rect):
    def __init__(self, 
                 screen: pygame.Surface,
                 topLeft: Vector2        = Vector2(0, 0), 
                 color: ColorLike        = "black",
                 thickness: int          =1):
        
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
    
    def getRandVec2(self) -> Vector2:
        x = np.random.randint(self.left, self.right)
        y = np.random.randint(self.top, self.bottom)
        return Vector2(x, y)

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
            distance = abs(self.position.y - self.radius - box.top )
            colTime  = distance/abs(self.velocity.y) + systemTime
            if colTime < self.wallCollision.time:
                self.wallCollision.set(WallSide.TOP, colTime)
        elif self.velocity.y > 0:
            distance = abs(self.position.y+self.radius - box.bottom)
            colTime  = distance/abs(self.velocity.y) + systemTime
            if colTime < self.wallCollision.time:
                self.wallCollision.set(WallSide.BOTTOM, colTime)
        
        # handle left/right box collision
        if self.velocity.x > 0:
            distance = abs(box.right - (self.position.x + self.radius))
            colTime  = distance/abs(self.velocity.x) + systemTime
            if colTime < self.wallCollision.time:
                self.wallCollision.set(WallSide.RIGHT, colTime)
        elif self.velocity.x < 0:
            distance = abs((self.position.x - self.radius) - box.left)
            colTime  = distance/abs(self.velocity.x) + systemTime
            if colTime < self.wallCollision.time:
                self.wallCollision.set(WallSide.LEFT, colTime)

        
    def resolveBoxCollision(self, box: BoundingBox) -> None:
        match self.wallCollision.side:
            case WallSide.TOP:
                self.velocity.y *= -1
                self.position.y  = box.top + self.radius
            case WallSide.BOTTOM:
                self.velocity.y *= -1
                self.position.y  = box.bottom - self.radius
            case WallSide.RIGHT:
                self.velocity.x *= -1
                self.position.x  = box.right - self.radius
            case WallSide.LEFT:
                self.velocity.x *= -1
                self.position.x  = box.left + self.radius
        

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
        sigma: float = partnerParticle.radius + self.radius
        b: float     = dR.dot(dV)
   
        dV_self  = + 2*(partnerParticle.mass/(self.mass + partnerParticle.mass)) * (b/(sigma))*dR.normalize()
        dV_other = - 2*(self.mass         /(self.mass   + partnerParticle.mass)) * (b/(sigma))*dR.normalize()
        self.velocity            += dV_self
        partnerParticle.velocity += dV_other
        

class CollisionSchedule:
    def __init__(self, 
                 _list: list = []):
        self.heap = _list
        if self.heap:
            heapq.heapify(self.heap)
    
    def put(self, particle: Particle) -> None:
        heapq.heappush(self.heap, particle)
        
    def pop(self) -> Particle:
        return heapq.heappop(self.heap)

    def pushPop(self, particle: Particle) -> Particle:
        return heapq.heappushpop(self.heap, particle)

    def heapify(self) -> None:
        heapq.heapify(self.heap)
    


def getRandVelocity(low: float, high: float) -> Vector2:
    x = np.random.randint(low, high)
    y = np.random.randint(low, high)
    return Vector2(x, y)


if __name__ == "__main__":

    pygame.init()
    screen        = pygame.display.set_mode((1024, 480))
    clock         = pygame.time.Clock()
    running       = True
    dt            = 0
    systemTime    = 0
    screen_size   = Vector2    (screen.get_size())
    box           = BoundingBox(screen    = screen,
                                topLeft   = 0.2*screen_size,
                                color     = "red",
                                thickness = 10)
    
    particleA     = Particle   (position = box.getRandVec2(),
                                velocity=Vector2(140/2, -125/2),
                                color="red")
    particleB     = Particle   (position = box.getRandVec2(),
                                velocity=Vector2(-120/2, +235/2),
                                color="blue")
    particleC     = Particle   (position = box.getRandVec2(),
                                velocity=Vector2(435/2, -75/2),
                                color="green")
        
    particles      = [particleA, particleB, particleC]
    collisionQueue = CollisionSchedule() #PriorityQueue()

    for p in particles:
        p.computeBoxCollisionTime(box, systemTime)
        p.computeParticleCollisionTime(particles, systemTime)
        p.setCollisionType()
        collisionQueue.put(p)
    
    collisionParticle = collisionQueue.pop()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for p in particles:
            p.update(dt)


        if (systemTime + dt) >= collisionParticle.getCollisionTime():
            # Handle priority collision depending if it is a wall reflection || particle collision
            
            if collisionParticle.collisionType == CollisionType.WALL:
                collisionParticle.resolveBoxCollision(box)
            elif collisionParticle.collisionType == CollisionType.PARTICLE:
                # Check if partner particle has not been updated in the meantime
                if  collisionParticle.isParticleCollisionValid():
                    print(f"Collision!")
                    # resolve particle Collision
                    collisionParticle.resolveParticleCollision()    
                    partner = collisionParticle.getCollisionPartner()
                    
                    # Record collision time for partner collisions...
                    partner.setLastCollisionTime(systemTime)
                    
                    # & compute futur collisions:
                    partner.computeBoxCollisionTime(box, systemTime)
                    partner.computeParticleCollisionTime(particles, systemTime)
                    partner.setCollisionType()
                    
                    # rearrange Queue
                    collisionQueue.heapify()
                else: 
                    print("[invalid collision], updating & getting new event.")
                
            # record time of last event, important for comparing collision validity
            collisionParticle.setLastCollisionTime(systemTime)
            
            # Compute new collision time for this particle
            collisionParticle.computeBoxCollisionTime(box, systemTime)
            collisionParticle.computeParticleCollisionTime(particles, systemTime)
            collisionParticle.setCollisionType()
            
            # Put "old" particle back in & get "new" particle with highest priority:
            collisionParticle = collisionQueue.pushPop(collisionParticle)
    
            name = ""
            if collisionParticle == particleA:
                name = "Red"
            elif collisionParticle == particleB:
                name = "Blue"
            elif collisionParticle == particleC:
                name = "Green"   
                
            if collisionParticle.collisionType == CollisionType.WALL:
                print(f"NEXT: {name}: {collisionParticle.collisionType} with {collisionParticle.wallCollision.side}")            
            else:
                partner = ""
                if collisionParticle.particleCollision.partner == particleA:
                    partner = "Red"
                elif collisionParticle.particleCollision.partner == particleB:
                    partner = "Blue"
                elif collisionParticle.particleCollision.partner == particleC:
                    partner = "Green"   
                print(f"NEXT: {name}: {collisionParticle.collisionType} with {partner}")    

        screen.fill("purple")
        box.draw()
        for p in particles:
            p.draw(screen)
                    
        pygame.display.flip()

        dt         = clock.tick(60) / 1000
        systemTime += dt
    pygame.quit()