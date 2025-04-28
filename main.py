from __future__ import annotations
import pygame
from pygame import Vector2
from collisionModules import CollisionType
from boundingBox import BoundingBox
from particle import Particle
from collisionScheduele import CollisionSchedule
 
if __name__ == "__main__":

    pygame.init()
    screen        = pygame.display.set_mode((1024, 480))
    clock         = pygame.time.Clock()
    running       = True
    dt            = 0
    radius        = 20
    systemTime    = 0
    screen_size   = Vector2    (screen.get_size())
    box           = BoundingBox(screen    = screen,
                                topLeft   = 0.2*screen_size,
                                color     = "red",
                                thickness = 10)
    
    particleA     = Particle   (position = box.getRandVec2(radius),
                                velocity = Particle.getRandVelocity(-200, 200),
                                color    = "red",
                                radius   = radius)
    particleB     = Particle   (position = box.getRandVec2(radius),
                                velocity = Particle.getRandVelocity(-200, 200),
                                color    = "blue",
                                radius   = radius)

    particleC     = Particle   (position = box.getRandVec2(radius),
                                velocity = Particle.getRandVelocity(-200, 200),
                                color    = "green",
                                radius   = radius)
        
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