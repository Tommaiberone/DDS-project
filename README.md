# DDS-project
 
Introduction

Distributed systems have become increasingly popular in recent years due to their ability to provide high
performance, fault-tolerance, and scalability. In a distributed system, multiple threads work together to
achieve a common goal, sharing resources and communicating with each other. Mutual exclusion is a
fundamental problem in distributed systems, where multiple threads compete for access to a shared
resource, such as a critical section.
Two mutual exclusion algorithms will be evaluated in this paper. Specifically, one is from Michel
Raynal’s paper “A Distributed Solution to the k-out of-M Resources Allocation Problem” and the other
one is from Kerry Raymond’s paper “A Distributed Algorithm for Multiple Entries to a Critical
Section”. Both algorithms are designed to solve extensions of the mutual exclusion problem.
The k-out of-M resources allocation problem taken into consideration by Raymond’s algorithm
considers a distributed system in which a set of M identical resources are shared between n threads. Each
of these resources can be used by at most one thread at a given time (i.e. in mutual exclusion).
Each thread P_i can request at once any number k_i of these M resources; this thread remains blocked
until it has got a set of k_i resources.
On the other hand, the problem that Raymond tackles is a bit different: the goal of his paper is to show
an algorithm that extends Ricart and Agrawala’s algorithm for distributed mutual exclusion to enable up
to K nodes to be within the critical section simultaneously.

Goal of the study

This study will start with a brief analysis of the two algorithms and their functioning. Then a particular
situation will be examined in which the two algorithms actually end up solving the same problem.
An analysis will be conducted on the behavior of the two algorithms in this specific setup, to investigate
how the performance of these two approaches compare when these parameters vary:
● Time spent in critical section: The time spent in the critical section affects the throughput of the
algorithm. It can be modified by setting a random interval for the time spent in the critical
section.
● Workload: The workload represents the rate of requests for the critical section or resources. This
parameter can be modified by setting different rates of requests.
The following metrics will be measured to evaluate the performance of the algorithms:


● Time to enter the critical section: This metric measures the time a thread waits before it can
enter the critical section.
● Number of messages: This metric measures the number of messages exchanged between threads
during the execution of the algorithm.
Then the dependability of the two algorithms will be analyzed, in particular wrt how they handle faults,
such as thread crashes, message losses, and network failures. The two approaches used by these
algorithms will also be briefly compared to other approaches found in the literature.