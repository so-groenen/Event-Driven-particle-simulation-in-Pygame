import heapq
from collisionModules import CollisionType
from particle import Particle


class CollisionSchedule:
    def __init__(self, 
                 _list: list[Particle] = []):
        self.heap = _list
        if self.heap:
            heapq.heapify(self.heap)
            
    def push(self, particle: Particle) -> None:
        heapq.heappush(self.heap, particle)
        
    def pop(self) -> Particle:
        return heapq.heappop(self.heap)

    def pushPop(self, particle: Particle) -> Particle:
        return heapq.heappushpop(self.heap, particle)

    def heapify(self) -> None:
        heapq.heapify(self.heap)
        
    def showVelocities(self) -> None:
        for i, p in enumerate(self.heap):
            print(f"{i}: v: {p.velocity}")
    
    @classmethod
    def showParticle(self, particle: Particle) -> None:
        if particle.collisionType == CollisionType.WALL:
                print(f"THIS: [WALL] collision Time: {particle.getCollisionTime():.5f}")
        else:
            partner = particle.getCollisionPartner()
            print(f"THIS: [PARTICULE] collision Time: {particle.getCollisionTime():.5f}, lastUpdate [{particle.lastCollisionTime}, partner: {partner.lastCollisionTime}] ")
    
    def showSchedule(self) -> None:
        partner: Particle = None
        for i, p in enumerate(self.heap):
            if p.collisionType == CollisionType.WALL:
                print(f"{i}: [WALL] collision Time: {p.getCollisionTime():.5f}")
            else:
                partner = p.getCollisionPartner()
                print(f"{i}: [PARTICULE] collision Time: {p.getCollisionTime():.5f}, lastUpdate [{p.lastCollisionTime}, partner: {partner.lastCollisionTime}] ")