import heapq
from particle import Particle


class CollisionSchedule:
    def __init__(self, 
                 _list: list = []):
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