from lib.config import Configuration
from twisted.internet import protocol

import simplejson as json

jConfig = Configuration()

class SocketHandler(protocol.Protocol):
    def connectionMade(self):
        print "connection from %s" % self.transport.getPeer()

    def connectionLost(self, reason):
        print "disconnected (%s)" % reason.getErrorMessage()

    def dataReceived(self, data):
            response = self.requestHandler(data.strip())
            if response != False:
                pass

    def requestHandler(self, request):
        try:
            data = json.loads(request)
        except:
            return '{"status": 0, "error": "invalid input format"}'

        if data.has_key('c'):
            command = data.get('c')
            if command == 'login':
                return None
            elif command == 'logout':
                return None
            else:
                return '{"status": 0, "error": "unknown command"}'
        else:
            return '{"status": 0, "error": "missing parameter: c (command)"}'

    # INSTRUCTION SET - Begin
    # INSTRUCTION SET - End
