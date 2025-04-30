# PygameEventDrivenCollisions
Event driven hard sphere elastic collisions using python Pygame-CE

A small Pygame prototype to showcase Event driven hard sphere particle collisions.

In the basic "time based" collisions, all pairs of particles are checked at all times for possible collisions (i.e. overlap), and handled right away.\
This introduces lots of looping over many particles pairs, even though particle will spend most of their time moving in straight line.

In contrast, in "event driven" collisions, a priority queue (for example using a "heap" implementation) of all particle collisions is created BEFORE the simulation start. Particles store information about their "next collision time", the corresponding "partner particle", as well as a "last updated time".\
The top priority "collision event" (ie, the particle with smallest collision time / first particle in the queue) is poped from the queue and the relevant particle-pair collision is handled.
Futur collisions involving the particle & the partner are computed, and the two particles are pushed back into the queue, using their new "collision times" as priority indicator.\
A new top priority "collision event" (particle) is then poped from the queue, and the process starts anew.\
Collisions with walls/boundaries are handled in a similar way.\
Some care should be taken however: When one particle "A" is schedueled to collide with another particle "B", but "B" has in the meantime collided, keeping track of the "last updated time" of both particles permits us to label this collision as "invalid": We simply compute new collisions for "A" and put it back into the queue.
Inbetween collisions, the particle motion is trivial: they move in a straight lines.\
A "real time event driven" variant can also be done: Collision detections is performed by checking when "systemTime+dt == collisionTime", the event is then handled, the particles updated, put back into the queue, and the next "collision event" is retrieved with a new collisionTime.

See: [Efficient event-driven simulations of hard spheres](https://arxiv.org/abs/2201.01100) by Frank Smallenburg for a comprehensive review. 
