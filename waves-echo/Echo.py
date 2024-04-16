import secrets
from enum import Enum
from typing import Any, Dict, List, Optional
from ...GenericModel import GenericModel, GenericMessageHeader, GenericMessagePayload, GenericMessage
from ...Generics import Event, EventTypes, logger

class EchoMessageTypes(Enum):
    START = "ECHO_START"
    MESSAGE = "ECHO_MESSAGE"

class EchoMessageHeader(GenericMessageHeader):
    def __init__(self, *args, token: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = token

class EchoMessagePayload(GenericMessagePayload):
    pass

class EchoMessage(GenericMessage):
    pass

class EchoNode:
    def __init__(self, id: int):
        self.id = id
        self.sent = False
        self.replied = False
    
    def __str__(self):
        return f"Node {self.id} Sent: {self.sent} Replied: {self.replied}"

class EchoTraverse(GenericModel):
    def __init__(self, componentname: str, componentinstancenumber: int, context: Optional[Dict] = None, configurationparameters: Optional[Dict] = None, num_worker_threads: int = 1, topology: Any = None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        self.token_neighbor: Dict[str, List[EchoNode]] = {}
        self.token_parent: Dict[str, int] = {}

    def on_message_from_bottom(self, eventobj: Event):
        msg = eventobj.eventcontent
        hdr = msg.header
        message_source = hdr.messagefrom
        logger.debug(f"OnMessageFromBottom received from {message_source}")

        payload: List[Any] = msg.payload.messagepayload

        if hdr.messagetype in (EchoMessageTypes.START, EchoMessageTypes.MESSAGE):
            logger.debug(f"Processing message {hdr.messagetype} from {message_source} to {hdr.messageto} ")
            self.process_message(hdr, message_source, payload)

    def process_message(self, hdr: EchoMessageHeader, message_source: int, payload: List[Any]):
        token = hdr.token
        if hdr.messagetype == EchoMessageTypes.START:
            self.token_parent[token] = -1

        parent = self.token_parent.get(token, message_source)
        self.token_parent.setdefault(token, message_source)

        for neighbor in self.get_neighbors(token):
            if neighbor.sent:
                continue
            neighbor.sent = True
            message = self.prepare_message(EchoMessageTypes.MESSAGE, neighbor.id, token, payload)
            self.send_down(Event(self, EventTypes.MFRT, message))

        for neighbor in self.get_neighbors(token):
            if neighbor.id == message_source:
                neighbor.replied = True
                break
        
        if all(n.replied for n in self.get_neighbors(token)):
            if parent == -1:
                logger.debug(f"Node {self.componentinstancenumber} has completed the traversal")
            else:
                payload.append(str(self.componentinstancenumber))
                message = self.prepare_message(EchoMessageTypes.MESSAGE, parent, token, payload)
                self.send_down(Event(self, EventTypes.MFRB, message))

    def start_traverse(self):
        token = self.create_token()
        self.send_self(Event(self, EventTypes.MFRB, self.prepare_message(EchoMessageTypes.START, self.componentinstancenumber, token, [])))
        logger.debug("Started traversal")

    def create_token(self) -> str:
        return secrets.token_hex(32)

    def create_neighbor_list(self) -> List[EchoNode]:
        neighbor_list = self.topology.get_neighbors(self.componentinstancenumber)
        return [EchoNode(n) for n in neighbor_list]
    
    def get_neighbors(self, token: str) -> List[EchoNode]:
        mapping = self.token_neighbor.get(token)
        if mapping == None:
            mapping = self.create_neighbor_list()
            self.token_neighbor[token] = mapping
        return mapping

    def prepare_message(self, message_type: EchoMessageTypes, neighbor: int, token: str, payload:Any = None) -> GenericMessage:
        header = EchoMessageHeader(message_type, self.componentinstancenumber, neighbor, neighbor, token=token)
        payload = EchoMessagePayload(payload)
        return EchoMessage(header, payload)
