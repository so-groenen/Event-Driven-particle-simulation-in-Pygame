# PygameEventDrivenCollisions
Event driven elastic collisions using python Pygame-CE

A small Pygame prototype to showcase Event driven particle collisions rather than time based collisions.
In "time based" collisions, all pairs of particle are checked at all times for possible collisions, and handled right away.
In contrast, in "event driven" collisions, a priority queue of all particle collisions is created BEFORE the simulation launch. The top priority collision event is poped from the queue
and as soon as the system time == collision time, the relevant particle-pair collision is handled, then futur collisions involving these particles are computed, and pushed back into the queue.
We then pop the new top priority collision event from the queue, and thus obtain a new futur collision event to be handled.

See: [Efficient event-driven simulations of hard spheres](https://arxiv.org/abs/2201.01100) by Frank Smallenburg for a comprehensive review. 
