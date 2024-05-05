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
    :caption: DFS Traversal Algorithm.

    Implements: DfsTraverse Instance: dfsTraverse
    Uses: AdhocComputing Network Model
    Events: Init, MessageFromBottom
    Needs:

    OnInit: () do
        Initialize token_neighbor and token_parent dictionaries
        If initiator then
            Generate a token using secrets.token_hex
            Set self token_parent for this token as -1
            Start traversal with token and empty payload
            Log "Started traversal"

    OnMessageFromBottom: (eventobj) do
        Extract message, header and payload from eventobj
        Log received message details
        If message type is START or FORWARD then
            Process the message with process_message function

    process_message: (hdr, message_source, payload) do
        Extract token and message type from header
        Set or update parent source for this token
        Determine parent based on existing token_parent value or message source
        Find the next unvisited neighbor that is not the parent or source
        Choose next target based on unvisited neighbors or backtrack to parent
        If next target is found then
            Append current node to payload
            Prepare and send message to next target
            Log action taken
        Else
            Log traversal completion and details

    select_next_target: (payload, unvisited_neighbor, parent_for_token) do
        If unvisited neighbor exists then
            Mark neighbor as visited
            Return neighbor id
        If no unvisited neighbors and parent is not -1 then
            Return parent for potential backtrack
        Else
            Log completion and return None

    get_neighbors: (token) do
        Retrieve or create list of neighboring nodes for the given token
        Return list of neighbors

    prepare_message: (message_type, neighbor, token, payload) do
        Create message header and payload
        Return new message

Example
~~~~~~~~

Consider a simple network where node A initiates the DFS traversal. Node A generates a unique token, and sends a "DFS_START" message to itself to begin the traversal. Upon processing this message (OnMessageFromTop), node A identifies its unvisited neighbors and sends a "DFS_FORWARD" message to one of them, say node B. Node B, upon receiving this message, marks itself as visited, sets A as its parent, and continues the process, sending "DFS_FORWARD" messages to its own unvisited neighbors, such as node C. If node C reaches a point where no unvisited neighbors are left, it may initiate a backtrack by sending messages upwards (OnMessageFromBottom), eventually reaching back to node A.

Correctness
~~~~~~~~~~~

The correctness of the DFS algorithm is established on its ability to comprehensively and non-repetitively visit all nodes in the network:

- **Safety**: Ensures no node is visited more than once, thus avoiding infinite loops or redundant communications. This is accomplished by marking nodes as visited upon their first encounter and by maintaining clear parent-child relationships to guide the traversal.

- **Liveness**: Guarantees that all nodes in the network will be visited, assuming all nodes are reachable from the initiator. This ensures the complete coverage of the network.

- **Fairness**: Each node has the opportunity to initiate traversal to its unvisited neighbors and to contribute to the traversal process by relaying backtrack messages, ensuring equitable participation across the network.

Complexity
~~~~~~~~~~

- **Message Complexity**: The total number of messages sent across the network is proportional to twice the number of edges, O(2E), assuming each edge is traversed twice (once in each direction) during the traversal and potential backtrack phases.

- **Computational Complexity**: The computational burden on each node involves processing incoming messages, deciding on the next unvisited neighbor to visit or whether to backtrack. This complexity is typically proportional to the degree of the node, denoted as O(d), where d represents the number of direct neighbors or connections a node has.
