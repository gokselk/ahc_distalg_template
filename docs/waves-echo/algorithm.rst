.. include:: substitutions.rst

|Waves-Echo|
=========================================



Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The concept of wave algorithms originated from the need to efficiently manage and coordinate distributed systems, where direct communication between all pairs of nodes is infeasible due to the network's scale or topology. The Echo algorithm demonstrates a structured approach to broadcasting and collecting information across a network, ensuring that each node participates in the decision-making process without the need for central coordination.

Related Work
    - Tarry’s Algorithm: One of the earliest traversal algorithms that made the initial work for subsequent developments in wave algorithms. Tarry's algorithm ensures that a token circulates through a network, visiting each node exactly once, thereby establishing a spanning tree. This algorithm is foundational for understanding the mechanics behind token circulation in distributed systems (Tarry, 1884).

    - Depth-First Search (DFS) in Distributed Systems: The adaptation of DFS principles to distributed computing has been instrumental in the development of algorithms that efficiently explore network topologies. This approach has influenced the design of algorithms that prioritize the exploration of unvisited nodes, significantly impacting how information is gathered and disseminated across a network (Awerbuch, 1985).

Distributed Algorithm: |Waves-Echo| 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: RST
    :linenos:
    :caption: Echo algorithm.
    

    Implements: WavesEcho Instance: we
    Uses: NetworkCommunication Instance: nc
    Events: Init, ReceiveMessage
    Needs:

    OnInit: () do
        For each neighbor do
            Trigger nc.SendMessage (neighbor, "StartMessage")

    OnReceiveMessage: (message, sender) do
        If first message from sender then
            Mark sender as parent
            For each neighbor except sender do
                Trigger nc.SendMessage (neighbor, "EchoMessage")
        If received messages from all neighbors then
            If not initiator then
                Trigger nc.SendMessage (parent, "DecisionMessage")
            Else
                Perform decision

Example
~~~~~~~~

Consider a network of five nodes arranged in a star topology, with the central node as the initiator. The Waves-Echo algorithm facilitates the collection and dissemination of information, ultimately leading to a decision made by the initiator after all nodes have communicated their status.

Correctness
~~~~~~~~~~~

The algorithm guarantees that all nodes in the network are reached, and a decision is made based on the collective input. This is achieved through the structured message passing and decision-making process inherent in the algorithm's design.


Complexity 
~~~~~~~~~~

The theoretical complexity of the Waves-Echo algorithm involves the number of messages proportional to twice the number of edges in the network, with a computational complexity that depends on the size of the network and its topology.

.. [Fokking2013] Wan Fokkink, Distributed Algorithms An Intuitive Approach, The MIT Press Cambridge, Massachusetts London, England, 2013
