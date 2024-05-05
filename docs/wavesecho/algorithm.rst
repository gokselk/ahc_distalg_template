.. include:: substitutions.rst

|WavesEcho|
=========================================



Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The concept of wave algorithms originated from the need to efficiently manage and coordinate distributed systems, where direct communication between all pairs of nodes is infeasible due to the network's scale or topology. The Echo algorithm demonstrates a structured approach to broadcasting and collecting information across a network, ensuring that each node participates in the decision-making process without the need for central coordination.

Related Work
    - Tarry's Algorithm: One of the earliest traversal algorithms that made the initial work for subsequent developments in wave algorithms. Tarry's algorithm ensures that a token circulates through a network, visiting each node exactly once, thereby establishing a spanning tree. This algorithm is foundational for understanding the mechanics behind token circulation in distributed systems (Tarry, 1884).

    - Depth-First Search (DFS) in Distributed Systems: The adaptation of DFS principles to distributed computing has been instrumental in the development of algorithms that efficiently explore network topologies. This approach has influenced the design of algorithms that prioritize the exploration of unvisited nodes, significantly impacting how information is gathered and disseminated across a network (Awerbuch, 1985).

Distributed Algorithm: |WavesEcho| 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: RST
    :linenos:
    :caption: Echo Algorithm.

    Implements: EchoTraverse Instance: echoTraverse
    Uses: AdhocComputing Network Model
    Events: Init, MessageFromBottom
    Needs:

    OnInit: () do
        Generate and store a unique token
        Send "ECHO_START" message to self to initiate the echo process
        Log "Started traversal"

    OnMessageFromBottom: (eventobj) do
        Extract the message, header, and payload from eventobj
        Log received message details
        If message type is "ECHO_START" or "ECHO_MESSAGE" then
            Process the message using the process_message function

    process_message: (hdr, message_source, payload) do
        Retrieve or set the parent based on the token
        Mark all unvisited neighbors and send them an "ECHO_MESSAGE"
        For each neighbor, check if they have replied, if not, continue to wait
        If all neighbors have replied:
            If this node has a parent then
                Append current node ID to payload
                Prepare and send an "ECHO_MESSAGE" back to the parent
            Else
                Log that this node has completed the traversal

    get_neighbors: (token) do
        Retrieve the list of neighboring nodes for the given token
        If no list exists, create it from the topology's neighbor data
        Return the list of neighbors

    prepare_message: (message_type, neighbor, token, payload) do
        Create a new message with specified parameters
        Return the newly created message


Example
~~~~~~~~

Consider a network consisting of five nodes configured in a star topology, where the central node serves as the initiator. Utilizing the Echo algorithm, this network engages in a process whereby information is systematically gathered from all peripheral nodes. Each node sends its status back to the central node, which aggregates these inputs to make a final decision. This setup demonstrates how the Echo algorithm efficiently handles data collection and decision-making within a centrally coordinated network structure.

Correctness
~~~~~~~~~~~

The Echo algorithm ensures complete and accurate information gathering from every node in the network. The structured sequential messaging and response mechanism ensures that every node is reached and can communicate its status back to the initiator. The correctness of this algorithm is upheld by the guaranteed delivery and processing of messages, which assures that a comprehensive decision is based on the data received from all nodes in the network.

Complexity 
~~~~~~~~~~

The message complexity of the Echo algorithm is theoretically proportional to twice the number of edges in the network. This is because each communication link is used twice—once for sending the initial message and once for receiving the echo. The computational complexity, however, is largely influenced by the network’s topology and size. In centralized structures like the star topology, the initiator node bears a higher computational load due to its role in processing incoming data from all other nodes, which is generally proportional to the number of connections it manages.
