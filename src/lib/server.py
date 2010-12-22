from socket import *
from twisted.internet import protocol

import random
import simplejson as json
import uuid

class SocketHandler(protocol.Protocol):
    def connectionMade(self):
        #print "connection from %s" % self.transport.getPeer().host
        pass

    def connectionLost(self, reason):
        #print "disconnected (%s)" % reason.getErrorMessage()
        if self.transport.getPeer().host in self.factory.workers:
            self.unregisterBySocket()

    def dataReceived(self, data):
        line = data.strip()
        if len(line) > 0:
            response = self.requestHandler(line)
            if response != None:
                self.transport.write(response + "\r\n");

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

            elif command == 'do-sync':
                return self.doSync(params.get('servers'), params.get('jobs'))

            elif command == 'notify':
                return self.notify(params.get('do'), params.get('name'))

            elif command == 'call':
                if params.get('bg') == False:
                    params['uuid'] = uuid.uuid1()

                return self.call(params.get('name'), params, params.get('bg'))

            elif command == 'remote':
                if params.has_key('uuid'):
                    if not params.has_key('source'):
                        params['source'] = self.transport.getPeer().host

                return self.remoteCall(params.get('name'), params, params.get('bg'))

            elif command == 'response':
                return self.response(data)

            else:
                return None
                #return '{"status": 0, "error": "unknown command"}'

        #else: return '{"status": 0, "error": "missing parameter: cmd (command)"}'
        return None

    # INSTRUCTION SET - Begin
    """
    This method starts the synchronization process and returns do-sync request including server and job lists
    """
    def sync(self):
        tempData = {
            'servers': self.factory.servers,
            'jobs'   : self.factory.jobs.get('remote')
        }
        if len(self.factory.jobs.get('local')) > 0:
            for job in self.factory.jobs.get('local'):
                if not tempData.get('jobs').has_key(job):
                    tempData.get('jobs')[job] = []

                # we need to convert local jobs to remote jobs by ip addresses
                if len(self.factory.jobs.get('local').get(job)) > 0:
                    for worker in self.factory.jobs.get('local').get(job):
                        ip = worker.transport.getPeer().host
                        if not ip in tempData.get('jobs').get(job):
                            tempData.get('jobs').get(job).append(ip)

        try:
            sync = socket(AF_INET, SOCK_STREAM)
            sync.connect((self.transport.getPeer().host, self.factory.configuration.get('port')))
            sync.send("%s\r\n" % json.dumps({
                'cmd'   : 'do-sync',
                'params': tempData
            }));
            sync.close()
        except:
            return None

        # add the synchronized server into server list
        if not self.transport.getPeer().host in self.factory.servers:
            self.factory.servers.append(self.transport.getPeer().host)

        del tempData
        return None

    """
    @param  List  servers: List of remote servers
    @param  Dict  jobs: List of remote jobs
    This method completes synchronization process
    """
    def doSync(self, servers, jobs):
        if len(servers) > 0:
            for server in servers:
                if not server in self.factory.servers:
                    self.factory.servers.append(server)

        # job list
        if len(jobs) > 0:
            for job in jobs:
                if job in self.factory.jobs.get('remote'):
                    if len(jobs.get(job)) > 0:
                        for server in jobs.get(job):
                            if not server in self.factory.jobs.get('remote').get(job):
                                if server == '127.0.0.1':
                                    server = self.transport.getPeer().host

                                self.factory.jobs.get('remote').get(job).append(server)
                else:
                    self.factory.jobs.get('remote')[job] = jobs.get(job)

        # add the synchronized server into server list
        if not self.transport.getPeer().host in self.factory.servers:
            self.factory.servers.append(self.transport.getPeer().host)

        return None

    """
    @param  String  name: Worker name
    This method adds a new job to local list and shares it with remote servers
    """
    def notify(self, do, name):
        ip = self.transport.getPeer().host

        if do == 'register':
            if not self.factory.job.get('remote').has_key(name):
                self.factory.job.get('remote')[name] = [ ip ]
            elif ip not in self.factory.job.get('remote').get(name):
                self.factory.job.get('remote').get(name).append(ip)

        elif do == 'unregister':
            if self.factory.job.get('remote').has_key(name):
                if ip in self.factory.job.get('remote').get(name):
                    self.factory.job.get('remote').get(name).remove(ip)

        return None

    """
    @param  String  name: Worker name
    This method adds a new job to local list and shares it with remote servers
    """
    def register(self, name):
        if self.transport.getPeer().host not in self.factory.workers:
            self.factory.workers.append(self.transport.getPeer().host)

        if not self.factory.jobs.get('local').has_key(name):
            self.factory.jobs.get('local')[name] = []

        if self.transport not in self.factory.jobs.get('local').get(name):
            self.factory.jobs.get('local').get(name).append(self)

        self.broadcast({
            'cmd'   : 'notify',
            'params': {
                'do'  : 'register',
                'name': name
            }
        })
        return None

    """
    @param  String  name: Worker name
    This method removes a job from local list by job name and shares it with remote servers
    """
    def unregisterByName(self, name):
        if self.factory.jobs.get('local').has_key(name):
            if self in self.factory.jobs.get('local').get(name):
                self.factory.jobs.get('local').get(name).remove(self)

        self.broadcast({
            'cmd'   : 'notify',
            'params': {
                'do'  : 'unregister',
                'name': name
            }
        })
        return None

    """
    This method removes jobs from local list by socket when connection closed with worker and shares it with remote servers
    """
    def unregisterBySocket(self):
        for job in self.factory.jobs.get('local'):
            if self in self.factory.jobs.get('local').get(job):
                self.factory.jobs.get('local').get(job).remove(self)

        # TODO: call synchronization method
        return None

    """
    @param  String  name: Worker name
    @param  JSON    params: Parameters
    @param  Boolean background: Request type
    This method finds a worker suitable with the request and sends the request to worker.
    """
    def call(self, name, params, background):
        worker = self.getWorkerTransport(name)
        if worker != None:
            if not background:
                self.factory.requests.get('local')[params.get('uuid')] = self

            worker.transport.write("%s\r\n" % json.dumps(params));
            return None

        worker = self.getWorkerSocket(name)
        if worker != None:
            if not background:
                self.factory.requests.get('local')[params.get('uuid')] = self

            worker.send("%s\r\n" % json.dumps({
                'cmd'   : 'remote',
                'params': json.dumps(params)
            }))
            worker.close()

        return None

    """
    @param  String  name: Worker name
    @param  JSON    params: Parameters
    @param  Boolean background: Request type
    This method finds a worker suitable with the request and sends the request to worker.
    """
    def remoteCall(self, name, params, background):
        worker = self.getWorkerTransport(name)
        if worker != None:
            if not background:
                self.factory.requests.get('remote')[params.get('uuid')] = self.transport.getPeer().host

            worker.transport.write("%s\r\n" % json.dumps(params));
            return None

        worker = self.getWorkerSocket(name)
        if worker != None:
            worker.send("%s\r\n" % json.dumps({
                'cmd'   : 'remote',
                'params': json.dumps(params)
            }))
            worker.close()

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
                self.factory.requests.get('local').get(process).transport.write("%s\r\n" % data.get('params'))
                del self.factory.requests.get('local')[process]

            elif self.factory.requests.get('remote').has_key(process):
                if data.get('params').has_key('source'):
                    ip = data.get('params').get('source')
                else:
                    ip = self.factory.requests.get('remote').get(process)

                del self.factory.requests.get('remote')[process]

                try:
                    client = socket(AF_INET, SOCK_STREAM)
                    client.connect((ip, self.factory.configuration.get('port')))
                    client.send("%s\r\n" % json.dumps({
                        'cmd'   : 'response',
                        'params': json.dumps(data.get('params'))
                    }))
                    client.close()
                except:
                    pass

            # else: unknown uuid!

        return None

    """
    @param  String  name: Worker name
    This method returns a worker connection suitable with the given job
    """
    def getWorkerTransport(self, name):
        if self.factory.jobs.get('local').has_key(name) and (len(self.factory.jobs.get('local')[name]) > 0):
            worker = random.sample(self.factory.jobs.get('local').get(name), 1)
            if len(worker) > 0:
                return worker[0]
            else:
                return None

        return None

    """
    @param  String  name: Worker name
    This method returns a worker socket suitable with the given job
    """
    def getWorkerSocket(self, name):
        if self.factory.jobs.get('remote').has_key(name) and (len(self.factory.jobs.get('remote')[name]) > 0):
            ip = random.sample(self.factory.jobs.get('remote').get(name), 1)
            try:
                worker = socket(AF_INET, SOCK_STREAM)
                worker.connect((ip, self.factory.configuration.get('port')))
                return worker
            except:
                if ip in self.factory.jobs.get('remote').get(name):
                    self.factory.jobs.get('remote').get(name).remove(ip)

                return self.getWorkerSocket(name)

        return None

    """
    @param  Object  message: Broadcast message
    This method broadcasts the given message to all remote servers
    """
    def broadcast(self, message):
        if len(self.factory.servers) > 0:
            for server in self.factory.servers:
                try:
                    client = socket(AF_INET, SOCK_STREAM)
                    client.connect((server, self.factory.configuration.get('port')))
                    client.send("%s\r\n" % json.dumps(message))
                    client.close()
                except:
                    pass

    # INSTRUCTION SET - End
