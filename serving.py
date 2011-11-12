# -*- coding: utf-8 -*- vim: set ts=4 sw=4 expandtab:
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2011  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the MIT style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from SocketServer import TCPServer
from werkzeug.serving import BaseWSGIServer
from werkzeug.serving import WSGIRequestHandler as BaseWSGIRequestHandler

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WSGIRequestHandler(BaseWSGIRequestHandler):
    pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class WSGILocalServer(BaseWSGIServer):
    RequestHandlerClass = WSGIRequestHandler
    def __init__(self, host, port, webapp, handler=None, *args, **kw):
        if handler is None:
            handler = self.RequestHandlerClass
        super(WSGILocalServer, self).__init__(
            host, port, webapp, handler, *args, **kw)

    def server_bind(self):
        """Override server_bind to store the server name."""
        # bypass HTTPServer.server_bind
        TCPServer.server_bind(self)
        self.setup_server_name()

    def setup_server_name(self):
        host, port = self.socket.getsockname()[:2]
        self.server_name = host
        self.server_port = port

    @classmethod
    def createWebAppServer(klass, webapp, host='127.0.0.1', port=0, *args, **kw):
        return klass(host, port, webapp, *args, **kw)

createWebAppServer = WSGILocalServer.createWebAppServer

