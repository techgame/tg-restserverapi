#!/usr/bin/env python
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from TG.restServerApi.urlDispatch import UrlDispatch

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class UrlDispatchQuickstart(object):
    """Port of the Werkzeug Url quickstart to url dispatcher"""
    api = UrlDispatch()

    def wsgi(self, environ, start_response):
        return self.api.wsgi(environ, start_response, self)
    __call__ = wsgi

    @api.route('/')
    def root(self, request):
        return 'root'

    @api.route('/about')
    def about(self, request):
        return 'about'

    @api.route('/<int:year>/')
    @api.route('/<int:year>/<int:month>/')
    @api.route('/<int:year>/<int:month>/<int:day>/')
    @api.route('/<int:year>/<int:month>/<int:day>/<slug>')
    def posts(self, request, year=None, month=None, day=None, slug=None):
        return 'posts %r' % ((year, month, day, slug),)

    @api.route('/feeds/')
    @api.route('/feeds/<feed_name>.rss')
    def feeds(self, request, feed_name):
        return 'feeds %r' % (feed_name,)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('127.0.0.1', 8090, UrlDispatchQuickstart())

