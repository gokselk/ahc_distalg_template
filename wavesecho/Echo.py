import secrets
from enum import Enum
from typing import Any, Dict, List, Optional
from adhoccomputing.GenericModel import GenericModel, GenericMessageHeader, GenericMessagePayload, GenericMessage
from adhoccomputing.Generics import Event, EventTypes, logger

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

class EchoTraverse(GenericModel):
    def __init__(self, componentname: str, componentinstancenumber: int, context: Optional[Dict] = None, configurationparameters: Optional[Dict] = None, num_worker_threads: int = 1, topology: Any = None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        self.token_neighbor: Dict[str, List[EchoNode]] = {}
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

            if hdr.messagetype in (EchoMessageTypes.START, EchoMessageTypes.MESSAGE):
                logger.debug(f"Processing message {hdr.messagetype} from {message_source} to {hdr.messageto} ")
                self.process_message(hdr, message_source, payload)

    def process_message(self, hdr: EchoMessageHeader, message_source: int, payload: List[Any]):
            """
            Process an incoming message.

            Args:
                hdr (EchoMessageHeader): The header of the incoming message.
                message_source (int): The source of the incoming message.
                payload (List[Any]): The payload of the incoming message.

            Returns:
                None
            """
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
            """
            Starts the traversal process by creating a token and sending a start message to the component instances.

            Returns:
                None
            """
            token = self.create_token()
            self.send_self(Event(self, EventTypes.MFRB, self.prepare_message(EchoMessageTypes.START, self.componentinstancenumber, token, [])))
            logger.debug("Started traversal")

    def create_token(self) -> str:
            """
            Generates a random token using secrets module.

            Returns:
                str: A random token in hexadecimal format.
            """
            return secrets.token_hex(32)

    def create_neighbor_list(self) -> List[EchoNode]:
            """
            Creates a list of EchoNode objects representing the neighbors of the current node.

            Returns:
                A list of EchoNode objects representing the neighbors of the current node.
            """
            neighbor_list = self.topology.get_neighbors(self.componentinstancenumber)
            return [EchoNode(n) for n in neighbor_list]
    
    def get_neighbors(self, token: str) -> List[EchoNode]:
            """
            Retrieves the list of neighboring EchoNodes for a given token.

            Args:
                token (str): The token for which to retrieve the neighbors.

            Returns:
                List[EchoNode]: The list of neighboring EchoNodes.
            """
            mapping = self.token_neighbor.get(token)
            if mapping == None:
                mapping = self.create_neighbor_list()
                self.token_neighbor[token] = mapping
            return mapping

    def prepare_message(self, message_type: EchoMessageTypes, neighbor: int, token: str, payload:Any = None) -> GenericMessage:
            """
            Prepares an Echo message with the given parameters.

            Args:
                message_type (EchoMessageTypes): The type of the Echo message.
                neighbor (int): The ID of the neighboring component.
                token (str): The token associated with the message.
                payload (Any, optional): The payload of the message. Defaults to None.

            Returns:
                GenericMessage: The prepared Echo message.
            """
            header = EchoMessageHeader(message_type, self.componentinstancenumber, neighbor, neighbor, token=token)
            payload = EchoMessagePayload(payload)
            return EchoMessage(header, payload)
