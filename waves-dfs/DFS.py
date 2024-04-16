import secrets
from enum import Enum
from typing import Any, Dict, List, Optional
from ...GenericModel import GenericModel, GenericMessageHeader, GenericMessagePayload, GenericMessage
from ...Generics import Event, EventTypes, logger

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
        msg = eventobj.eventcontent
        hdr = msg.header
        message_source = hdr.messagefrom
        logger.debug(f"OnMessageFromBottom received from {message_source}")

        payload: List[Any] = msg.payload.messagepayload

        if hdr.messagetype in (DfsMessageTypes.FORWARD, DfsMessageTypes.START):
            self.process_message(hdr, message_source, payload)

    def process_message(self, hdr: DfsMessageHeader, message_source: int, payload: List[Any]):
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
        token = self.create_token()
        self.send_self(Event(self, EventTypes.MFRB, self.prepare_message(DfsMessageTypes.START, self.componentinstancenumber, token, [])))
        logger.debug("Started traversal")

    def create_token(self) -> str:
        return secrets.token_hex(32)

    def create_neighbor_list(self) -> List[DfsNode]:
        neighbor_list = self.topology.get_neighbors(self.componentinstancenumber)
        return [DfsNode(n, False) for n in neighbor_list]
    
    def get_neighbors(self, token: str) -> List[DfsNode]:
        mapping = self.token_neighbor.get(token)
        if mapping == None:
            mapping = self.create_neighbor_list()
            self.token_neighbor[token] = mapping
        return mapping

    def prepare_message(self, message_type: DfsMessageTypes, neighbor: int, token: str, payload:Any = None) -> GenericMessage:
        header = DfsMessageHeader(message_type, self.componentinstancenumber, neighbor, neighbor, token=token)
        payload = DfsMessagePayload(payload)
        return DfsMessage(header, payload)
