# PygameEventDrivenCollisions
Event driven elastic collisions using python Pygame-CE

A small Pygame prototype to showcase Event driven particle collisions rather than time based collisions.

In "time based" collisions, all pairs of particles are checked at all times for possible collisions, and handled right away.\
In contrast, in "event driven" collisions, a priority queue of all particles collisions is created BEFORE the simulation launch. Particles store information about their next collision time, as well as the involved "partner particle".\
The top "priority collision event" (ie, the particle with smallest collision time) is poped from the queue and as soon as the "systemTime == collisionTime", the relevant particle-pair collision is handled.
Futur collisions involving the particle & the partner are computed, and the two particles are pushed back into the queue, using their new "collision times" as priority indicator.
A new top priority collision event (particle) is then poped from the queue, and the process starts a new.\
Collisions with wall are handled in a similar way.

See: [Efficient event-driven simulations of hard spheres](https://arxiv.org/abs/2201.01100) by Frank Smallenburg for a comprehensive review. 
