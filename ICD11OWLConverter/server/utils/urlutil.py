# -*- coding: utf-8 -*-
# Copyright (c) 2014, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
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

from urllib.parse import urlsplit, parse_qs, urlunsplit, urlencode
from cherrypy import request, HTTPRedirect
import configparser
import sys
from os.path import join

config = configparser.ConfigParser()
config.read(join(sys.path[0], 'settings.conf'))
section = 'href_settings'

dropParms = ['bypass', 'user', 'password']


def redirect(reluri):
    """ Instruct the client to redirect to the supplied relative URI
    @param reluri: relative URI to redirect to
    """
    raise HTTPRedirect(base_uri() + '/' + reluri)

def base_uri():
    """ Return the base URI - up to the root of the service without an additional parameters
        that get you to the service itself.  This is used to create URL's to ancillary
        files and support services.

        Must be accessed in the context of a cherrypy request
    """
    return config[section]['host'] + config[section]['root']


def completeuri_sans_parms():
    """ Return the complete URI of this call sans parms """
    return base_uri() + request.path_info


def complete_uri():
    """ Return the complete URI that invoked this call """
    return strip_control_params(
        completeuri_sans_parms() + (('?' + request.query_string) if request.query_string else ''))


def relative_uri():
    """ Return the relative URI that invoked this call """
    return config[section]['root'] + request.path_info


def strip_control_params(url):
    """ Remove any control parameters from a URL that should not be forwarded.
        This includes user ids, passwords and bypass parameters
    """
    spliturl = urlsplit(url)
    urlparms = parse_qs(spliturl.query, True)
    for d in dropParms:
        urlparms.pop(d, None)
    splitlist = list(spliturl)
    splitlist[3] = urlencode(urlparms, True)
    if '@' in splitlist[1]: splitlist[1] = splitlist[1].split('@')[1]
    return urlunsplit(splitlist)


def append_params(base_uri, parms):
    """ Append a parameter to the base URI
    @param base_uri: The uri to append the parameters to
    @type base_uri: c{URI}

    @param parms: the list of parameters to append
    @type parms: c{dict}
    """
    spliturl = urlsplit(base_uri)
    urlparms = parse_qs(spliturl.query,True)
    for (k,v) in parms.items():
        urlparms[k] = v
    splitlist = list(spliturl)
    splitlist[3] = urlencode(urlparms, True)
    return urlunsplit(splitlist)


def remove_params(baseuri, parms):
    """ Remove parameter or parameters from the base URI
     @param baseuri: The uri to append the parameters to
     @type baseuri: c{URI}

    @param parms: the list of parameters to remove
    @type parms: c{list} or c{string}
    """
    if not isinstance(parms, (list, tuple)):
        parms = [parms]
    spliturl = urlsplit(baseuri)
    urlparms = parse_qs(spliturl.query, True)
    for k in parms:
        urlparms.pop(k, None)
    splitlist = list(spliturl)
    splitlist[3] = urlencode(urlparms, True)
    return urlunsplit(splitlist)



