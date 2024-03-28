.. include:: substitutions.rst

|Waves-Echo|
=========================================



Background and Related Work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Present any background information survey the related work. Provide citations.

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
