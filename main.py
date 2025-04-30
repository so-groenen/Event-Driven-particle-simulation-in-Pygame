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
    fps: float          = 0 
    radius: float       = 2.5
    systemTime: float   = 0.0
    dt: float           = 0.0    
    particleNumber: int = 750
    minVel: float       = -20.0
    maxVel: float       = 20.0
    
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


    Particle.MonteCarloSortInBox(particles, box)
    Particle.removeCenterOfMass(particles)
    collisionQueue = CollisionSchedule()
    
    lastColTime    = 0
    colTime        = 0

    for p in particles:
        p.setPrecision(1E-10)
        p.computeBoxCollisionTime(box, systemTime)
        p.computeParticleCollisionTime(particles, systemTime)
        p.setCollisionType()
        collisionQueue.push(p)
        
    # Set to 10: use the setPrecision method to change it. It is 1E-10 initially.
    PrecisionDecimalPlaces  = particles[0].getPrecisionDecimalPlaces() 
    # First event:
    collisionParticle = collisionQueue.pop()
    print("Simulation Start.")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Event managing: We only draw Wall collisions & valid particle collisions, hence we loop until we get one.
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
        drawFps(screen, font)
        # Particle.drawEnergyAvg(screen, font, particles, (screen_size.x/2, 0))

        for p in particles:
            p.draw(screen)
                    
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()