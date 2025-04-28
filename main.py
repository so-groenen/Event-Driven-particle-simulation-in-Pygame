from __future__ import annotations
import pygame
from pygame import Vector2
from collisionModules import CollisionType
from boundingBox import BoundingBox
from particle import Particle
from collisionSchedule import CollisionSchedule
 
if __name__ == "__main__":

    pygame.init()
    screen            = pygame.display.set_mode((1024, 480))
    clock             = pygame.time.Clock()
    running           = True
    fps: float        = 200.0
    dt: float         = 1.0 / fps
    radius: float     = 5.0
    systemTime: float = 0.0
    particleNumber    = 50
    minVel: float     = -200.0
    maxVel: float     = 200.0
    
    screen_size   = Vector2    (screen.get_size())
    box           = BoundingBox(screen    = screen,
                                topLeft   = 0.2*screen_size,
                                color     = "red",
                                thickness = 10)
    
    particles      = [Particle(position = Vector2(0, 0),
                                velocity = Particle.getRandVelocity(minVel, maxVel),
                                color    = "blue",
                                radius   = radius) 
                      for _ in range(particleNumber)]

    Particle.MonteCarloSortInBox(particles, box)

    collisionQueue = CollisionSchedule()
    for p in particles:
        p.computeBoxCollisionTime(box, systemTime)
        p.computeParticleCollisionTime(particles, systemTime)
        p.setCollisionType()
        collisionQueue.push(p)
    
    collisionParticle = collisionQueue.pop()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for p in particles:
            p.update(dt)


        if (systemTime + dt/2.0) >= collisionParticle.getCollisionTime():
            # Handle priority collision depending if it is a wall reflection || particle collision
            
            if collisionParticle.collisionType == CollisionType.WALL:
                collisionParticle.resolveBoxCollision(box)
            elif collisionParticle.collisionType == CollisionType.PARTICLE:
                # Check if partner particle has not been updated in the meantime
                if  collisionParticle.isParticleCollisionValid():

                    # resolve particle Collision (also handles partner velocity change)
                    collisionParticle.resolveParticleCollision()    

                    # Record collision time for partner collisions...
                    partner = collisionParticle.getCollisionPartner()                    
                    partner.setLastCollisionTime(systemTime)
                    
                    # & compute futur collisions for partner:
                    partner.computeBoxCollisionTime(box, systemTime)
                    partner.computeParticleCollisionTime(particles, systemTime)
                    partner.setCollisionType()
                    
                    # rearrange Queue
                    collisionQueue.heapify()
                    
                
            # record time of last event, important for comparing collision validity
            collisionParticle.setLastCollisionTime(systemTime)
            
            # Compute new collision time for this particle
            collisionParticle.computeBoxCollisionTime(box, systemTime)
            collisionParticle.computeParticleCollisionTime(particles, systemTime)
            collisionParticle.setCollisionType()
            
            # Put "old" particle back in & get "new" particle with highest priority:
            collisionParticle = collisionQueue.pushPop(collisionParticle)
    
   

        screen.fill("purple")
        box.draw()
        for p in particles:
            p.draw(screen)
                    
        pygame.display.flip()

        # dt          = clock.tick(60) / 1000
        clock.tick(fps)
        systemTime += dt
    pygame.quit()