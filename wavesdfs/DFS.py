import secrets
from enum import Enum
from typing import Any, Dict, List, Optional
from adhoccomputing.GenericModel import GenericModel, GenericMessageHeader, GenericMessagePayload, GenericMessage
from adhoccomputing.Generics import Event, EventTypes, logger

class DfsMessageTypes(Enum):
    START = "DFS_START"
    FORWARD = "DFS_FORWARD"

class DfsMessageHeader(GenericMessageHeader):
    def __init__(self, *args, token: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = token

class DfsMessagePayload(GenericMessagePayload):
    pass

class DfsMessage(GenericMessage):
    pass

class DfsNode:
    def __init__(self, id: int, visited: bool):
        self.id = id
        self.visited = visited

class DfsTraverse(GenericModel):
    def __init__(self, componentname: str, componentinstancenumber: int, context: Optional[Dict] = None, configurationparameters: Optional[Dict] = None, num_worker_threads: int = 1, topology: Any = None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        self.token_neighbor: Dict[str, List[DfsNode]] = {}
        self.token_parent: Dict[str, int] = {}

    def on_message_from_bottom(self, eventobj: Event):
            """
            Handles the 'on_message_from_bottom' event.

            Args:
                eventobj (Event): The event object containing the message.

            Returns:
                None
            """
            msg = eventobj.eventcontent
            hdr = msg.header
            message_source = hdr.messagefrom
            logger.debug(f"OnMessageFromBottom received from {message_source}")

            payload: List[Any] = msg.payload.messagepayload

            if hdr.messagetype in (DfsMessageTypes.FORWARD, DfsMessageTypes.START):
                self.process_message(hdr, message_source, payload)

    def process_message(self, hdr: DfsMessageHeader, message_source: int, payload: List[Any]):
        """
        Process an incoming message.

        Args:
            hdr (DfsMessageHeader): The header of the incoming message.
            message_source (int): The source of the incoming message.
            payload (List[Any]): The payload of the incoming message.

        Returns:
            None
        """
        token = hdr.token
        if hdr.messagetype == DfsMessageTypes.START:
            self.token_parent[token] = -1

        parent = self.token_parent.get(token, message_source)
        self.token_parent.setdefault(token, message_source)

        unvisited_neighbor = next((
            n for n in self.get_neighbors(token)
            if not n.visited and n.id != parent and n.id != message_source)
        , None)

        next_target = self.select_next_target(payload, unvisited_neighbor, parent)
        if next_target is not None:
            payload.append(str(self.componentinstancenumber))
            message = self.prepare_message(DfsMessageTypes.FORWARD, next_target, token, payload)
            self.send_down(Event(self, EventTypes.MFRT, message))

    def select_next_target(self, payload: List[Any], unvisited_neighbor: Optional[DfsNode], parent_for_token: int) -> Optional[int]:
        """
        Selects the next target node for traversal in the Depth-First Search algorithm.

        Args:
            payload (List[Any]): The payload data associated with the current node.
            unvisited_neighbor (Optional[DfsNode]): The unvisited neighbor node to be selected as the next target.
            parent_for_token (int): The ID of the parent node to be selected as the next target if no unvisited neighbor is available.

        Returns:
            Optional[int]: The ID of the selected target node, or None if traversal is completed.

        """
        if unvisited_neighbor:
            chosen_neighbor = unvisited_neighbor
            chosen_neighbor.visited = True
            return chosen_neighbor.id
        elif parent_for_token != -1:
            return parent_for_token
        else:
            logger.debug(f"Traversal completed in {len(payload)} hops with {self.topology.G.number_of_edges()} edges.")
            return None

    def start_traverse(self):
            """
            Starts the traversal process by creating a token and sending a start message to itself.

            Returns:
                None
            """
            token = self.create_token()
            self.send_self(Event(self, EventTypes.MFRB, self.prepare_message(DfsMessageTypes.START, self.componentinstancenumber, token, [])))
            logger.debug("Started traversal")

    def create_token(self) -> str:
        """
        Generates a random token using secrets module.

        Returns:
            str: A random token in hexadecimal format.
        """
        return secrets.token_hex(32)

    def create_neighbor_list(self) -> List[DfsNode]:
        """
        Creates a list of DfsNode objects representing the neighbors of the current node.

        Returns:
            A list of DfsNode objects representing the neighbors of the current node.
        """
        neighbor_list = self.topology.get_neighbors(self.componentinstancenumber)
        return [DfsNode(n, False) for n in neighbor_list]
    
    def get_neighbors(self, token: str) -> List[DfsNode]:
        """
        Retrieves the list of neighboring DfsNodes for a given token.

        Args:
            token (str): The token for which to retrieve the neighbors.

        Returns:
            List[DfsNode]: The list of neighboring DfsNodes.
        """
        mapping = self.token_neighbor.get(token)
        if mapping == None:
            mapping = self.create_neighbor_list()
            self.token_neighbor[token] = mapping
        return mapping

    def prepare_message(self, message_type: DfsMessageTypes, neighbor: int, token: str, payload:Any = None) -> GenericMessage:
        header = DfsMessageHeader(message_type, self.componentinstancenumber, neighbor, neighbor, token=token)
        payload = DfsMessagePayload(payload)
        return DfsMessage(header, payload)
