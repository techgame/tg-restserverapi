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

import functools
from werkzeug.exceptions import MethodNotAllowed, HTTPException, NotFound
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class UrlDispatch(object):
    RuleClass = Rule
    MapClass = Map

    def __init__(self, db={}, rules=[]):
        self.db = db.copy()
        self.rules = rules[:]

    @classmethod
    def new(klass, *args, **kw): return klass(*args, **kw)
    def branch(self): return self.new(self.db, self.rules)
    def route(self, *args, **kw):
        RuleClass = kw.get('RuleClass', self.RuleClass)
        methods = kw.get('methods')
        if isinstance(methods, basestring):
            kw['methods'] = [m.upper() for m in methods.split()]
        def deco_route(func):
            endpoint = kw.get('endpoint')
            if endpoint is None:
                endpoint = self.endpointForFunc(func)
                kw['endpoint'] = endpoint
            rule = RuleClass(*args, **kw)
            self.addRoute(endpoint, rule, func)
            return func
        return deco_route
    def endpointForFunc(self, func): return func.__name__

    def GET(self, *args, **kw):
        kw['methods'] = ['GET', 'HEAD']
        return self.route(*args, **kw)
    def PUT(self, *args, **kw):
        kw['methods'] = ['PUT']
        return self.route(*args, **kw)
    def POST(self, *args, **kw):
        kw['methods'] = ['POST']
        return self.route(*args, **kw)
    def DELETE(self, *args, **kw):
        kw['methods'] = ['DELETE']
        return self.route(*args, **kw)

    def addRoute(self, endpoint, rule, func):
        self._url_map = None
        self.rules.append(rule)
        self.db[endpoint] = rule, func
        func.routes = getattr(func, 'routes', []) + [(endpoint, rule)]
        return endpoint

    _url_map = None
    def getUrl_map(self):
        r = self._url_map
        if r is None:
            r = self.MapClass(self.rules)
            self._url_map = r
        return r
    url_map = property(getUrl_map)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def findEndpointDispatch(self, endpoint, NotFoundException=NotFound):
        try: ep = self.db[endpoint]
        except LookupError:
            if NotFoundException is False:
                return None
            elif NotFoundException:
                raise NotFoundException(endpoint)
            else: raise
        return ep

    partial = staticmethod(functools.partial)
    def bindEndpoint(self, endpoint, epArgs, *args, **kw):
        rule, func = self.findEndpointDispatch(endpoint)
        if kw: epArgs.update(kw)
        return self.partial(func, *args, **epArgs)

    def dispatch(self, request, *args, **kw):
        res = None
        urls = self.url_map.bind_to_environ(request.environ)
        responder = self.firstResponders.get(request.method)
        try:
            if responder is not None:
                res = responder(self, urls, request)

            if res is None:
                endpoint, epArgs = urls.match()
                fnEndpoint = self.bindEndpoint(endpoint, epArgs, *args, **kw)
                res = fnEndpoint(request)

            if not callable(res):
                res = self.adaptToResponse(request, res)

            self.applyHeaders(request, res)
        except HTTPException as err:
            res = err
        return res

    firstResponders = {}

    def _firstResponder_options(self, urls, request):
        methods = urls.allowed_methods()
        if "OPTIONS" in methods: 
            return None # defer to explicit response from user
        if methods:
            methods = list(methods)
            if 'GET' in methods and 'HEAD' not in methods:
                methods.append('HEAD')
            if 'OPTIONS' not in methods:
                methods.append('OPTIONS')
        else: methods = ['GET', 'HEAD', 'OPTIONS']

        res = request.Response()
        res.allow.update(methods)
        return res
    firstResponders['OPTIONS'] = _firstResponder_options

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Request = Request
    Request.Response = Response
    def wsgi(self, environ, start_response, *args, **kw):
        request = self.Request(environ, start_response)
        res = self.dispatch(request, *args, **kw)
        return res(environ, start_response)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def adaptToResponse(self, request, res):
        return Response(res)

    def applyHeaders(self, request, response, headers=None):
        if headers is None:
            headers = self.findStdHeaders(request, response)
        return self.applyResponseHeaders(response, headers)

    def findStdHeaders(self, request, response):
        return {}

    def applyResponseHeaders(self, response, headers):
        try: setkv = response.headers.setdefault
        except AttributeError: pass
        else:
            for k,v in headers.iteritems():
                setkv(k, v)
        return response

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ UrlApiRoot
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class BasicApiRoot(object):
    def wsgi(self, environ, start_response):
        return self.api.wsgi(environ, start_response, self)

    def createServer(self, host='127.0.0.1', port=0, *args, **kw):
        from .serving import createWebAppServer
        return createWebAppServer(self.wsgi, host, port, *args, **kw)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class UrlApiRoot(BasicApiRoot):
    api = UrlDispatch()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Example
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if 1:
    class ExampleUrlApiRoot(UrlApiRoot):
        api = UrlApiRoot.api.branch()

        @api.route('/', methods='GET POST')
        def root(self, request):
            return request.Response('Success!', 200)

    del ExampleUrlApiRoot

