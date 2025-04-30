from collisionSchedule import CollisionSchedule
from particle import Particle

DEBUG: bool = False

def logMsg(string: str) -> None:
    if DEBUG:
        print(string)

def showCollisionSchedule(dt: float, collisionQueue: CollisionSchedule, currentCollisionParticle: Particle) -> None:
    if DEBUG and not dt:
        CollisionSchedule.showParticle(currentCollisionParticle)
        collisionQueue.showSchedule() 
 