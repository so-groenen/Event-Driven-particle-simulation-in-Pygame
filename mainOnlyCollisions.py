from __future__ import annotations
import pygame
from pygame import Vector2
from collisionModules import CollisionType
from boundingBox import BoundingBox
from particle import Particle
from collisionSchedule import CollisionSchedule
import debug

def drawFps(screen: pygame.Surface, font: pygame.Font):
    fps   = str(int(clock.get_fps()))
    fps_t = font.render(fps , 1, pygame.Color("RED"))
    screen.blit(fps_t,(0,0))
     
debug.DEBUG = False
if __name__ == "__main__":

    pygame.init()
    font                = pygame.font.SysFont("Arial" , 18 , bold = True)
    screen              = pygame.display.set_mode((1024, 480))
    clock               = pygame.time.Clock()
    running: bool       = True
    fps: float          = 1000
    radius: float       = 5
    systemTime: float   = 0.0
    dt: float           = 0.0    
    particleNumber: int = 150
    minVel: float       = -20
    maxVel: float       = 20 
    
    screen_size   = Vector2    (screen.get_size())
    box           = BoundingBox(screen    = screen,
                                topLeft   = 0.1*screen_size,
                                color     = "red",
                                thickness = 5)
    
    particles      = [Particle(position = Vector2(0, 0),
                                velocity = Particle.getRandVelocity(minVel, maxVel),
                                color    = "blue",
                                radius   = radius) 
                      for _ in range(particleNumber)]

    # Set to 10: use the setPrecision method to change it. It is 1E-10 initially.
    PrecisionDecimalPlaces  = particles[0].getPrecisionDecimalPlaces() 
    
    Particle.MonteCarloSortInBox(particles, box)
    Particle.removeCenterOfMass(particles)
    collisionQueue = CollisionSchedule()
    
    lastColTime    = 0
    colTime        = 0

    for p in particles:
        p.computeBoxCollisionTime(box, systemTime)
        p.computeParticleCollisionTime(particles, systemTime)
        p.setCollisionType()
        collisionQueue.push(p)
    
    # First event:
    collisionParticle = collisionQueue.pop()
    print("Simulation Start.")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        collisionTime = collisionParticle.getCollisionTime()
        dt            = round(collisionTime-lastColTime, PrecisionDecimalPlaces) 
        systemTime   += dt

        debug.logMsg(f"time since last collision: {dt}")
        debug.showCollisionSchedule(dt, collisionQueue, collisionParticle)
        
        for p in particles:
            p.update(dt)
     
        if collisionParticle.collisionType == CollisionType.WALL:
            collisionParticle.resolveBoxCollision(box)
            debug.logMsg("WALL COLLISION")
        elif collisionParticle.collisionType == CollisionType.PARTICLE:
            # Check if partner particle has not been updated in the meantime
            if collisionParticle.isParticleCollisionValid():
                debug.logMsg("PARTICLE COLLISION")
                # resolve particle Collision (also handles partner velocity change)
                collisionParticle.resolveParticleCollision()    
                
                # Record collision time for partner collisions...
                partner = collisionParticle.getCollisionPartner()               
                partner.setLastCollisionTime(systemTime)
                
                # ...& compute futur collisions for partner:
                partner.computeBoxCollisionTime(box, systemTime)
                partner.computeParticleCollisionTime(particles, systemTime)
                partner.setCollisionType()
                
                # rearrange Queue
                collisionQueue.heapify()
            else:
                debug.logMsg("INVALID PARTICLE COLLISION")
                
                
        # record time of last event, important for comparing collision validity
        collisionParticle.setLastCollisionTime(systemTime)
        lastColTime = systemTime

        # Compute new collision time for this particle
        collisionParticle.computeBoxCollisionTime(box, systemTime)
        collisionParticle.computeParticleCollisionTime(particles, systemTime)
        collisionParticle.setCollisionType()

        # Put "old" particle back in & get "new" particle with highest priority:
        collisionParticle = collisionQueue.pushPop(collisionParticle)


        screen.fill("purple")
        box.draw()
        drawFps(screen, font)
        # Particle.drawEnergyAvg(screen, font, particles, (screen_size.x/2, 0))

        for p in particles:
            p.draw(screen)
                    
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()