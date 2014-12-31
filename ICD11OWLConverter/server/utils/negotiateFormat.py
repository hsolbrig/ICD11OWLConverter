# -*- coding: utf-8 -*-
# Copyright (c) 2013, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     Redistributions of source code must retain the above copyright notice, this
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
from server.utils.kwutil import *
from server.utils.listutils import listify

# A map between a format identifier and the equivalent mime types that come in the header
format_map = {'txt': 'text/plain',
              'html': ('text/html', 'application/xhtml+xml'),
              'htm': ('text/html', 'application/xhtml+xml'),
              'xhtml': ('application/xhtml+xml', 'text/xml', 'application/xml'),
              'xml': ('text/xml', 'application/xml', 'application/rdf+xml'),
              'pretty-xml': ('text/xml', 'application/xml', 'application/rdf+xml'),
              'json': 'application/json',
              'trix': 'application/trix',
              'n3': 'application/n-triples',
              'nquads': 'application/n-quads',
              'turtle':('text/turtle',),
              'nt': 'application/nt-triples',}


def negotiate_format(formats, rqst_header):
    matchlist = []
    for k in formats:
        matchlist += (listify(format_map.get(k, 'txt/plain')))
    bm = best_match(matchlist,
                     kwget(['Accept'], rqst_header, preference_order, 'text/html'))
    if bm:
        for me in format_map.items():
            if bm in listify(me[1]):
                return me[0]
    return 'html'