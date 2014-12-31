# -*- coding: utf-8 -*-
# Copyright (c) 2014, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the <ORGANIZATION> nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

import cherrypy
import types

from server.utils import negotiateFormat, listutils

htmlHead = "<!DOCTYPE html>"

# Return format map.  Browsers don't understand some of the fancier types
return_map = {'txt': 'text/plain',
              'html': 'text/html',
              'htm': 'text/html',
              'xhtml': 'application/xhtml+xml',
              'xml': 'application/rdf+xml',
              'pretty-xml': 'application/rdf+xml',
              'json': 'application/rdf+xml',
              'trix': 'application/rdf+xml',
              'n3': 'text/plain',
              'nquads': 'text/plain',
              'turtle': 'text/plain',
              'nt': 'text/plain',}


def expose(arg1=None, arg2=None):
    """ Expose the wrapped function as a web service
    :param arg1: Either a function or the "self" parameter for a class method or a set of allowable methods
    :param arg2: allowable methods if arg1 is "self"
    :return: normalized function wrapper
    """

    def expose_(func_):

        @cherrypy.tools.allow(methods=arg2)
        @cherrypy.expose
        def wrapped_f(self, *args, format=None, **kwargs):

            if not format:
                format = negotiateFormat.negotiate_format(self.formats, cherrypy.request.headers)


            # Function can return one of:
            # formatted string           - to be returned directly to the caller, unformatted
            # class                      - assumed to have a toxml() function
            # tuple                      - tuple of (rval, (error code, error message))
            #                               rval is string or class as above
            rtn = func_(self, *args, format=format, **kwargs)

            rval, (err, msg) = rtn if isinstance(rtn, (list, tuple)) else (rtn, (500, 'Internal Server Error'))
            if not rval:
                raise cherrypy.HTTPError(err, str(msg))
            if rval.startswith(htmlHead):
                return rval
            cherrypy.response.headers['Content-type'] = return_map.get(format, 'text/plain') + ';charset=UTF-8'
            return rval

        return wrapped_f

    # This can be invoked within a class, meaning that the first argument (
    if isinstance(arg1, (types.FunctionType, types.MethodType)):
        return expose_(arg1)
    elif arg1 is not None:
        arg2 = arg1
    return expose_

