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
"""

from lib.server import SocketHandler
from twisted.internet import reactor, protocol

factory = protocol.ServerFactory()

# Server Configuration - BEGIN
factory.configuration = {
    "debug": False,
    "port": 9000,
    "server": None,
    "plugin": {}
}
# Server Configuration - END

# Don't touch the rest of all the code

# if value is None we need to call synchronization method
factory.sync = None
# we must change it with a Boolean value as confliction

factory.servers = []
factory.jobs = {
    "local": {},
    "remote": {}
}
factory.requests = {
    "local": {},
    "remote": {}
}

factory.protocol = SocketHandler
reactor.listenTCP(factory.configuration.get("port"), factory)
reactor.run()
