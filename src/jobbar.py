"""
    Jobbar: Distributed Job Server Project
    Umut Aydin, me@umut.mobi
    http://jobbarserver.org

    Copyright (c) 2010 Umut Aydin
    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
    sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
    FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
    WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

    {"cmd": "sync", "params": {}}
    {"cmd": "register", "params": {"name": "just-do-it"}}
    {"cmd": "call", "params": {"name": "just-do-it", "bg": true, "params": {"user": 1001, "path": "/tmp/user-1001.log"}}}
"""

from lib.server import SocketHandler
from twisted.internet import reactor, protocol

import socket

factory = protocol.ServerFactory()

# You can change configuration parameters here.

# Server Configuration - BEGIN
factory.configuration = {
    "debug": False,
    "port": 9000,
    "server": None,
    "plugin": {}
}
# Server Configuration - END

# Don't touch the rest of the code

factory.servers = []
factory.jobs = {
    "local": {},
    "remote": {}
}
factory.requests = {
    "local": {},
    "remote": {}
}

# Synchronization Process- BEGIN
if factory.configuration.get("server") != None:
    factory.servers.append(factory.configuration.get("server"))
    try:
        sync = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sync.bind((factory.configuration.get("server"), factory.configuration.get("port")))
        sync.send("{\"cmd\": \"sync\"}, \"params\": {}\r\n");
        response = sync.recv()
        sync.close()

        if response:
            # update factory!!
            pass

    except:
        # job server is not reachable at the moment
        pass
# Synchronization Process- END

factory.protocol = SocketHandler
reactor.listenTCP(factory.configuration.get("port"), factory)
reactor.run()
