.. include:: substitutions.rst

|WavesDFS|
=========================================



Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The concept of wave algorithms originated from the need to efficiently manage and coordinate distributed systems, where direct communication between all pairs of nodes is infeasible due to the network's scale or topology. The DFS algorithm demonstrates a structured approach to broadcasting and collecting information across a network, ensuring that each node participates in the decision-making process without the need for central coordination.

Related Work
    - Tarry's Algorithm: One of the earliest traversal algorithms that made the initial work for subsequent developments in wave algorithms. Tarry's algorithm ensures that a token circulates through a network, visiting each node exactly once, thereby establishing a spanning tree. This algorithm is foundational for understanding the mechanics behind token circulation in distributed systems (Tarry, 1884).

    - Depth-First Search (DFS) in Distributed Systems: The adaptation of DFS principles to distributed computing has been instrumental in the development of algorithms that efficiently explore network topologies. This approach has influenced the design of algorithms that prioritize the exploration of unvisited nodes, significantly impacting how information is gathered and disseminated across a network (Awerbuch, 1985).

Distributed Algorithm: |WavesDFS| 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: RST
    :linenos:
    :caption: DFS algorithm.
    
    Implements: WavesDFS Instance: wdfs
    Uses: NetworkCommunication Instance: nc
    Events: Init, MessageFromBottom, MessageFromTop
    Needs:
    
    OnInit: () do
        Set parent to None
        Set isVisited to False
        If isInitiator then
            isVisited = True
            For each neighbor do
                Trigger nc.SendMessage (neighbor, "DFSStart")
    
    OnMessageFromTop: (message, sender) do
        If message is "DFSStart" and not isVisited then
            Set isVisited to True
            Set parent to sender
            For each neighbor except sender do
                Trigger nc.SendMessage (neighbor, "DFSStart")
        If no unvisited neighbors left then
            If parent is not None then
                Trigger nc.SendMessage (parent, "DFSBacktrack")
                
    OnMessageFromBottom: (message, sender) do
        If message is "DFSBacktrack" then
            If parent is not None then
                Trigger nc.SendMessage (parent, "DFSBacktrack")


Do not forget to explain the algorithm line by line in the text.

Example
~~~~~~~~

Consider a simple network where node A starts the DFS algorithm. Node A sends a message to its child node B. When node B receives this message (OnMessageFromTop), it broadcasts the message to its children, say node C. If node C wants to respond or send information back, it triggers OnMessageFromBottom, sending the message upwards through the network, eventually reaching node A.

Correctness
~~~~~~~~~~~

The correctness of the WavesDFS algorithm is established on its ability to visit all nodes in the network without repetition. It maintains two main properties:

Safety: No node is visited more than once, preventing infinite loops or redundant communications.
Liveness: Every node in the network will be visited, ensuring complete traversal.

Fairness is maintained by ensuring that each node has an equal opportunity to send and receive messages, contributing to the traversal process.


Complexity 
~~~~~~~~~~

Message Complexity: The total number of messages sent across the network is proportional to the number of edges in the network, denoted as O(E), since each edge is traversed at most twice (once in each direction).

Computational Complexity: The computational load on each node involves processing incoming messages and deciding on the traversal path. This is generally proportional to the degree of the node, denoted as O(d), where d is the degree of the node (the number of direct neighbors).