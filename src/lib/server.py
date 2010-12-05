from twisted.internet import protocol

import simplejson as json

class SocketHandler(protocol.Protocol):
    def connectionMade(self):
        print self.transport.doWrite()
        print "connection from %s" % self.transport.getPeer().host

    def connectionLost(self, reason):
        print "disconnected (%s)" % reason.getErrorMessage()

    def dataReceived(self, data):
        response = self.requestHandler(data.strip())
        if response != None:
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
        if not self.factory.jobs.get("local").has_key(name):
            self.factory.jobs.get("local").put(name, [])

        if self.transport not in self.factory.jobs.get("local").get(name):
            self.factory.jobs.get("local").get(name).append(self.transport)

        # call synchronization method

    """
    @param  String  name: Worker name
    This method removes a job from local list by job name and shares it with remote servers
    """
    def unregisterByName(self, name):
        if self.factory.jobs.get("local").has_key(name):
            #if self.transport in self.factory.jobs.get("local").get(name):
            self.factory.jobs.get("local").get(name).remove(self.transport)

        # call synchronization method

    """
    This method removes jobs from local list by socket when connection closed with worker and shares it with remote servers
    """
    def unregisterBySocket(self):
        for job in self.factory.jobs.get("local"):
            self.factory.jobs.get("local").get(job).remove(self.transport)

        # call synchronization method

    """
    @param  String  name: Worker name
    @param  JSON    params: Parameters
    @param  Boolean background: Job type
    This method finds a worker suitable with the request and sends the request to worker.
    """
    def call(self, name, params, background):
        worker = self.getWorkerSocket(name)
        if worker != False:
            if not background:
                self.factory.requests.get("local").put(params.get("uid"), self.transport)

            worker.write(json.dumps(params));
            return None
        else:
            return '{"status": 0, "error": "unknown job request"}'

    """
    @param  JSON    data: Worker response
    This method handles worker response for regular job requests.
    Background job requests have no response.
    """
    def response(self, data):
        pass

    """
    @param  String  name: Worker name
    This method returns a transport instance suitable with the given job
    """
    def getWorkerSocket(self, name):
        return False
    # INSTRUCTION SET - End
