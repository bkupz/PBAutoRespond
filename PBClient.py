# Brandon Kupczyk

from ws4py.client.threadedclient import WebSocketClient


class PBClient(WebSocketClient):
    """
    This class extends WebSocketClient and when a message is received via the web socket it is added to the queue.
    """
    my_queue = None

    def init_queue(self, queue):
        self.my_queue = queue

    def received_message(self, m):
        text = m.data.decode("utf-8") 
        self.my_queue.put(text)
