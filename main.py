from __future__ import annotations
import pygame
from pygame import Vector2
from collisionModules import CollisionType
from boundingBox import BoundingBox
from particle import Particle
from collisionSchedule import CollisionSchedule
from helper import drawFps
import debug

     
debug.DEBUG = False
if __name__ == "__main__":

    pygame.init()
    font                = pygame.font.SysFont("Arial" , 18 , bold = True)
    screen              = pygame.display.set_mode((1024, 480))
    clock               = pygame.time.Clock()
    running: bool       = True
    fps: float          = 0         # No fps limit
    radius: float       = 3       
    systemTime: float   = 0.0
    dt: float           = 0.0       # the time between collisions is dynamical: each frame corresponds to a collision event
    particleNumber: int = 500       
    minVel: float       = -20.0
    maxVel: float       = 20.0
    
    screenSize    = Vector2    (screen.get_size())
    box           = BoundingBox(screen    = screen,
                                topLeft   = 0.1*screenSize,
                                color     = "red",
                                thickness = 5)
     
    particles      = [Particle(position = Vector2(0, 0),
                                velocity = Particle.getRandVelocity(minVel, maxVel),
                                color    = "blue",
                                radius   = radius) 
                      for _ in range(particleNumber)]


    Particle.MonteCarloSortInBox(particles, box)
    Particle.removeCenterOfMass(particles)
    collisionQueue = CollisionSchedule()
    
    lastColTime    = 0
    colTime        = 0

    for p in particles:
        p.setPrecision(1E-10)                                      # Precision is set to 10 decimal places, used for comparing particle "update times".
        p.computeBoxCollisionTime(box, systemTime)
        p.computeParticleCollisionTime(particles, systemTime)
        p.setCollisionType()
        collisionQueue.push(p)
        
    # Precision is set to 10 decimal places. Used for rounding up time "dt" between collisions
    PrecisionDecimalPlaces  = particles[0].getPrecisionDecimalPlaces() 

    # First event:
    collisionParticle = collisionQueue.pop()
    
    print("Simulation Start.")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Event managing: We only draw wall collisions & valid particle collisions, hence we loop until we get one.
        while True:
            collisionTime = collisionParticle.getCollisionTime()
            dt            = round(collisionTime-lastColTime, PrecisionDecimalPlaces) 
            systemTime   += dt
            for p in particles:
               p.update(dt)
     
            if collisionParticle.collisionType == CollisionType.WALL:
                debug.logMsg("WALL COLLISION")
                collisionParticle.resolveBoxCollision(box)
                collisionParticle.computeNextEvent(particles, box, systemTime)
                
                collisionParticle = collisionQueue.pushPop(collisionParticle)
                lastColTime       = systemTime
                break
            elif collisionParticle.collisionType == CollisionType.PARTICLE:
                # Check if partner particle has not been updated in the meantime
                if collisionParticle.isParticleCollisionValid():
                    debug.logMsg("PARTICLE COLLISION")
                    collisionParticle.resolveParticleCollision()    
                    partner = collisionParticle.getCollisionPartner()         
                        
                    partner.computeNextEvent(particles, box, systemTime)
                    collisionQueue.heapify()
                    
                    collisionParticle.computeNextEvent(particles, box, systemTime)
                    collisionParticle = collisionQueue.pushPop(collisionParticle)
                    lastColTime       = systemTime
                    break
                else:
                    debug.logMsg("INVALID PARTICLE COLLISION")  
                    debug.showCollisionSchedule(dt, collisionQueue, collisionParticle)
                    
                    collisionParticle.computeNextEvent(particles, box, systemTime)
                    collisionParticle = collisionQueue.pushPop(collisionParticle)
                    lastColTime       = systemTime

        screen.fill("purple")
        box.draw()
        drawFps(screen, font, clock)

        for p in particles:
            p.draw(screen)
                    
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()