from __future__ import annotations
import pygame
from pygame import Vector2
from collisionModules import CollisionType
from boundingBox import BoundingBox
from particle import Particle
from collisionSchedule import CollisionSchedule
import debug


debug.DEBUG = True
if __name__ == "__main__":


    pygame.init()
    screen        = pygame.display.set_mode((1024, 480))
    clock         = pygame.time.Clock()
    running       = True
    dt            = 0
    radius        = 20
    systemTime    = 0
    minVelocity   = -200
    maxvelocity   = 200
    screen_size   = Vector2    (screen.get_size())
    box           = BoundingBox(screen    = screen,
                                topLeft   = 0.2*screen_size,
                                color     = "red",
                                thickness = 10)
    particleRed   =    Particle(position = box.getRandVec2(radius),
                                velocity = Particle.getRandVelocity(minVelocity, maxvelocity),
                                color    = "red",
                                radius   = radius)
    particleBlue  =    Particle(position = box.getRandVec2(radius),
                                velocity = Particle.getRandVelocity(minVelocity, maxvelocity),
                                color    = "blue",
                                radius   = radius)

    particleGreen =    Particle(position = box.getRandVec2(radius),
                                velocity = Particle.getRandVelocity(minVelocity, maxvelocity),
                                color    = "green",
                                radius   = radius)
        
    particles      = [particleRed, particleBlue, particleGreen]
    collisionQueue = CollisionSchedule()
    lastColTime    = 0
    deltaColTime   = 0
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


        if (systemTime + dt) >= collisionParticle.getCollisionTime():
            # Handle priority collision depending if it is a wall reflection || particle collision
            deltaColTime  = systemTime - lastColTime
            debug.logMsg(f"Time since last event: {deltaColTime:.3f}s.")
            if collisionParticle.collisionType == CollisionType.WALL:
                debug.logMsg("WALL COLLISION")
                collisionParticle.resolveBoxCollision(box)
                
            elif collisionParticle.collisionType == CollisionType.PARTICLE:
                # Check if partner particle has not been updated in the meantime
                if  collisionParticle.isParticleCollisionValid():
                    debug.logMsg("PARTICLE COLLISION")
                    # resolve particle Collision
                    collisionParticle.resolveParticleCollision()    
                    partner = collisionParticle.getCollisionPartner()
                    
                    # Record collision time for partner collisions...
                    partner.setLastUpdatedTime(systemTime)
                    # & compute futur collisions:
                    partner.computeBoxCollisionTime(box, systemTime)
                    partner.computeParticleCollisionTime(particles, systemTime)
                    partner.setCollisionType()
                    # rearrange Queue
                    collisionQueue.heapify()
                else: 
                    debug.logMsg("[invalid collision], updating & getting new event.")
                
            # record time of last event, important for comparing collision validity
            collisionParticle.setLastUpdatedTime(systemTime)
            # Compute new collision time for this particle
            collisionParticle.computeBoxCollisionTime(box, systemTime)
            collisionParticle.computeParticleCollisionTime(particles, systemTime)
            collisionParticle.setCollisionType()
            
            # Put "old" particle back in & get "new" particle with highest priority:
            collisionParticle = collisionQueue.pushPop(collisionParticle)
            lastColTime       = systemTime

            name = ""
            if collisionParticle == particleRed:
                name = "Red"
            elif collisionParticle == particleBlue:
                name = "Blue"
            elif collisionParticle == particleGreen:
                name = "Green"   
                
            if collisionParticle.collisionType == CollisionType.WALL:
                debug.logMsg(f"NEXT: {name}: {collisionParticle.collisionType} with {collisionParticle.wallCollision.side}")            
            else:
                partner = ""
                if collisionParticle.getCollisionPartner()  == particleRed:
                    partner = "Red"
                elif collisionParticle.getCollisionPartner() == particleBlue:
                    partner = "Blue"
                elif collisionParticle.getCollisionPartner() == particleGreen:
                    partner = "Green"   
                debug.logMsg(f"NEXT: {name}: {collisionParticle.collisionType} with {partner}")    

        screen.fill("purple")
        box.draw()
        for p in particles:
            p.draw(screen)

                    
        pygame.display.flip()

        dt         = clock.tick(60) / 1000
        systemTime += dt
    pygame.quit()