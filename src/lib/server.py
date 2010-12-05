from twisted.internet import protocol

import simplejson as json

class SocketHandler(protocol.Protocol):
    def __init__(self):
        print "instance created!"

    def connectionMade(self):
        print "connection from %s" % self.transport.getPeer()

    def connectionLost(self, reason):
        print "disconnected (%s)" % reason.getErrorMessage()

    def dataReceived(self, data):
            response = self.requestHandler(data.strip())
            if response != False:
                self.transport.write(response);

    def requestHandler(self, request):
        try:
            data = json.loads(request)
        except:
            return '{"status": 0, "error": "invalid input format"}'

        if data.has_key('cmd'):
            command = data.get('cmd')
            if command == 'register':
                return None
            elif command == 'unregister':
                return None
            elif command == 'call':
                return None
            elif command == 'response':
                return None
            else:
                return '{"status": 0, "error": "unknown command"}'
        else:
            return '{"status": 0, "error": "missing parameter: cmd (command)"}'

    # INSTRUCTION SET - Begin
    """
    @param  String  name: Worker name
    This method adds a new job to local list and shares it with remote servers
    """
    def register(self, name):
        pass

    """
    @param  String  name: Worker name
    This method removes a job from local list by job name and shares it with remote servers
    """
    def unregisterByName(self, name):
        pass

    """
    This method removes jobs from local list by socket when connection closed with worker and shares it with remote servers
    """
    def unregisterBySocket(self):
        pass

    """
    @param  String  name: Worker name
    @param  JSON    params: Parameters
    @param  Boolean background: Job type
    This method finds a worker suitable with the reuqest and sends the request to worker.
    """
    def call(self, name, params, background):
        pass

    """
    @param  JSON    data: Worker response
    This method handles worker response for regular job requests.
    Background job requests have no response.
    """
    def response(self, data):
        pass
    # INSTRUCTION SET - End
