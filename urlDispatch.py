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
from werkzeug.exceptions import HTTPException, NotFound
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

    def new(klass, *args, **kw): return klass(*args, **kw)
    def branch(self): return self.new(self.db, self.rules)
    def route(self, *args, **kw):
        RuleClass = kw.get('RuleClass', self.RuleClass)
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

    def findDispatch(self, environ, NotFoundException=NotFound):
        urls = self.url_map.bind_to_environ(environ)
        endpoint, kwArgs = urls.match()
        try: ep = self.db[endpoint]
        except LookupError:
            if NotFoundException is None: raise
            elif NotFoundException:
                raise NotFoundException(endpoint)
            else: ep = None
        return ep, kwArgs

    partial = staticmethod(functools.partial)
    def bindDispatchEx(self, request, args, kw):
        (rule, func), kwDisp = self.findDispatch(request.environ)
        if kw: kwDisp.update(kw)
        return self.partial(func, *args, **kwDisp)

    def dispatch(self, request, *args, **kw):
        fnEndpoint = self.bindDispatchEx(request, args, kw)
        return fnEndpoint(request)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Request = Request
    Request.Response = Response
    def wsgi(self, environ, start_response, *args, **kw):
        request = self.Request(environ, start_response)
        try: 
            res = self.dispatch(request, *args, **kw)
            if not callable(res):
                res = self.adaptToResponse(request, res)
        except HTTPException as err:
            res = err
        return res(environ, start_response)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def adaptToResponse(self, request, res):
        return Response(res)

