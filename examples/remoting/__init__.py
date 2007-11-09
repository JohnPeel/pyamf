# -*- encoding: utf8 -*-
#
# Copyright (c) 2007 The PyAMF Project. All rights reserved.
# 
# Nick Joyce
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

@author: U{Nick Joyce<mailto:nick@boxdesign.co.uk>}
"""

import os, os.path

def run_wsgi(options, services):
    """
    Runs the services using the L{pyamf.gateway.wsgi.WSGIGateway}

    @param services: List of services for the Flash gateway
    @type services: dict
    @param port: Port to run the server on
    @type port: int
    @return The function that will run the server
    @rettype callable
    """
    from pyamf.gateway.wsgi import WSGIGateway
    from wsgiref import simple_server

    gw = WSGIGateway(services)

    httpd = simple_server.WSGIServer(
        ('',int(options.port)),
        simple_server.WSGIRequestHandler,
    )

    httpd.set_app(gw)

    return httpd.serve_forever

def run_twisted(options, services):
    """
    Runs the services using the L{pyamf.gateway.twistedmatrix.TwistedGateway}

    @param services: List of services for the Flash gateway
    @type services: dict
    @param port: Port to run the server on
    @type port: int
    @return The function that will run the server
    @rettype callable
    """
    from twisted.internet import reactor
    from twisted.web import server, static, resource

    from pyamf.gateway.twistedmatrix import TwistedGateway

    gw = TwistedGateway(services)
    root = resource.Resource()

    root.putChild('', gw)
    root.putChild('/gateway', gw)
    root.putChild('crossdomain.xml', static.File(os.path.join(
        os.getcwd(), os.path.dirname(__file__), 'crossdomain.xml'),
        defaultType='application/xml'))

    reactor.listenTCP(int(options.port), server.Site(root))

    return reactor.run

def run_server(name, options, services):
    if options.server == 'wsgi':
        print "Started %s WSGI server on port %d" % (name, int(options.port))
        func = run_wsgi(options, services)
    elif options.server == 'twisted':
        print "Started %s Twisted server on port %d" % (name, int(options.port))
        func = run_twisted(options, services)

    func()

def parse_args(args):
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-s', '--server', dest='server',
        choices=('wsgi', 'twisted',), default='wsgi',
        help='Determines which server type to use')
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
        default=False)
    parser.add_option('-p', '--port', dest='port', default=8000)

    return parser.parse_args(args)
