from twisted.internet import protocol

import random
import simplejson as json
import uuid

# TODO: check string literals!
class SocketHandler(protocol.Protocol):
    def connectionMade(self):
        #print "connection from %s" % self.transport.getPeer().host
        pass

    def connectionLost(self, reason):
        #print "disconnected (%s)" % reason.getErrorMessage()
        self.unregisterBySocket()

    def dataReceived(self, data):
        line = data.strip()
        if len(line) > 0:
            response = self.requestHandler(line)
            if response != None:
                self.transport.write(response + "\n\r");

    def requestHandler(self, request):
        try:
            data = json.loads(request)
        except:
            return None
            #return '{"status": 0, "error": "invalid input format"}'

        if data.has_key('params'):
            params = data.get('params')
        else:
            return None
            #return '{"status": 0, "error": "missing parameter: params (parameters)"}'

        if data.has_key('cmd'):
            command = data.get('cmd')
            if command == 'register':
                return self.register(params.get('name'))

            elif command == 'unregister':
                return self.unregisterByName(params.get('name'))

            elif command == 'sync':
                return self.sync()

            elif command == 'call':
                if params.get('bg') == False:
                    params['uuid'] = uuid.uuid1()

                return self.call(params.get('name'), params, params.get('bg'))

            elif command == 'response':
                return self.response(data)

            else:
                return None
                #return '{"status": 0, "error": "unknown command"}'
        #else: return '{"status": 0, "error": "missing parameter: cmd (command)"}'

    # INSTRUCTION SET - Begin
    def sync(self):
        self.transport.write();


    """
    @param  String  name: Worker name
    This method adds a new job to local list and shares it with remote servers
    """
    def register(self, name):
        if not self.factory.jobs.get('local').has_key(name):
            self.factory.jobs.get('local')[name] = []

        if self.transport not in self.factory.jobs.get('local').get(name):
            self.factory.jobs.get('local').get(name).append(self)

        # call synchronization method
        return None

    """
    @param  String  name: Worker name
    This method removes a job from local list by job name and shares it with remote servers
    """
    def unregisterByName(self, name):
        if self.factory.jobs.get('local').has_key(name):
            #if self.transport in self.factory.jobs.get("local").get(name):
            self.factory.jobs.get('local').get(name).remove(self)

        # call synchronization method
        return None

    """
    This method removes jobs from local list by socket when connection closed with worker and shares it with remote servers
    """
    def unregisterBySocket(self):
        for job in self.factory.jobs.get('local'):
            self.factory.jobs.get('local').get(job).remove(self)

        # call synchronization method
        return None

    """
    @param  String  name: Worker name
    @param  JSON    params: Parameters
    @param  Boolean background: Request type
    This method finds a worker suitable with the request and sends the request to worker.
    """
    def call(self, name, params, background):
        worker = self.getWorkerSocket(name)
        if worker != None and (len(worker) == 1):
            if not background:
                self.factory.requests.get('local')[params.get('uuid')] = self

            worker.transport.write(json.dumps(params));

        #else: return '{"status": 0, "error": "unknown job request"}'
        return None

    """
    @param  JSON    data: Worker response
    This method handles worker response for regular job requests.
    Background job requests have no response.
    """
    def response(self, data):
        if data.get('params').has_key('uuid'):
            process = data.get('params').get('uuid')
            if self.factory.requests.get('local').has_key(process):
                del data.get('params')['uuid']
                self.factory.requests.get('local').get(process)[process].transport.write(data.get('params'))
                del self.factory.requests.get('local').get(process)[process]

            # else: unknown uuid!

        return None

    """
    @param  String  name: Worker name
    This method returns a transport instance suitable with the given job
    """
    def getWorkerSocket(self, name):
        if self.factory.jobs.get('local').has_key(name) and (len(self.factory.jobs.get('local')[name]) > 0):
            worker = random.sample(self.factory.jobs.get('local').get(name), 1)
            if len(worker) > 0:
                # Still connected? If not we need to call this method again!
                return worker[0]
            else:
                return None

        return None
    # INSTRUCTION SET - End
