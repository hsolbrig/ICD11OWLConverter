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

import socket
from py4j.java_gateway import JavaGateway, GatewayClient, Py4JNetworkError


def gwfunction(func):
    """ Function wrapper that handles making sure the connection is live and active
    :param func: Function to invoke when gateway is connected
    """
    def wrapped_f(self, *args, **kwargs):
        if self.gatewayconnected():
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                print(e)
                self.reconnect()
                return func(self, *args, **kwargs)
    return wrapped_f


class SCTConverterGateway(object):
    def __init__(self, port=25321):
        """ Construct a new SNOMED CT Converter/classifier gateway.  This uses the py4j gateway to connect to a java server.

        @param port: py4j gateway port (default: 25321)
        """
        self._gwPort = int(port)
        self._parser = None
        self._gateway = None
        self.reconnect()

    def reconnect(self):
        """ (Re)establish the gateway connection
        @return: True if connection was established
        """
        print("Connecting to the compositional grammar gateway on port: %s" % self._gwPort)
        try:
            self._gateway = JavaGateway(GatewayClient(port=self._gwPort))
            self._parser = self._gateway.jvm.org.mayo.parserpy.GatewayParser.parser
        except (socket.error, Py4JNetworkError) as e:
            print(e)
            self._gateway = None
            return False
        return True

    def gatewayconnected(self, reconnect=True):
        """ Determine whether the gateway is connected
        @param reconnect: True means try to reconnect if not connected
        @return: True if the gateway is active
        """
        return self._gateway is not None or (reconnect and self.reconnect())

    @gwfunction
    def parse(self, subj, primitive, cgstring):
        """ Parse the supplied compositional grammar string into OWL
        :param subj: subject URI
        :param primitive: if True, cgstring will be interpreted as subClassOf.  If False, equivalentClass
        :param cgstring: string to be interpreted
        :return:  OWL equivalent or None if an error
        """
        rval = self._parser.cgparse(subj, primitive, cgstring)
        return str(rval) if rval else None