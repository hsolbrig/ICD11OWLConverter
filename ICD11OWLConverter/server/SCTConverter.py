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
# Redistributions in binary form must reproduce the above copyright notice,
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
import re
import sys
from os.path import join
from rdflib import ConjunctiveGraph
from rdflib.plugin import plugins
from rdflib.serializer import Serializer
from server.BaseNode import expose
from ConverterGateway import SCTConverterGateway
from cgtoowl import parse_and_load, serialize_graph, add_namespaces, map_namespace

true_values = ['y', 'yes', 'true', '1', 'on', 'yup']
false_values = ['n', 'no', 'false', '0', 'off', 'nope']

htmldir = join(sys.path[0], 'static', 'html')
htmltext = open(join(htmldir, 'icd11.html')).read()

class formats():
    fmtbox = '<input type="radio" name="format" value="%s">%s</input>'


    def html_formats(self):
        return '\n'.join([self.fmtbox % (e, e) for e in self._formats])

class SCTConverter():

    def __init__(self):
        self._parser = SCTConverterGateway()
        self.formats = [e.name for e in plugins(kind=Serializer) if '/' not in e.name]

    @staticmethod
    def boolval(parm):
        parm_ = str(parm).lower()
        return True if parm_ in true_values else False if parm_ in false_values else None

    fmtbox = '<input type="radio" name="format" value="%s">%s</input>'

    def html_formats(self):
        return '\n'.join([self.fmtbox % (e, e) for e in self.formats])


    @expose
    def index(self, **_):
        subject = "who:12345"
        expr = """18526009| Disorder of appendix (disorder) |+
	302168000| Inflammation of large intestine (disorder) |+
	64572001| Disease (disorder) |:
	{ 116676008| Associated morphology (attribute) |=23583003| Inflammation (morphologic abnormality) |,
	363698007| Finding site (attribute) |=66754008| Appendix structure (body structure) | }"""
        formats = self.html_formats()
        return htmltext % vars()

    @expose(("POST", "GET"))
    def default(self, subject='', expr='', primitive=False, shorturis=False, removesct=False, format="n3", **_):
        subject = map_namespace(subject)
        primitive = self.boolval(primitive)
        shorturis = self.boolval(shorturis)
        removesct = self.boolval(removesct)
        expr = re.sub(r'\s+', '', expr, flags=re.DOTALL)
        g = add_namespaces(ConjunctiveGraph())
        if parse_and_load(self._parser, subject, primitive, expr, g):
            return serialize_graph(g, removesctid=removesct, shorturi=shorturis, format=format)
        return None, (400, "Unable to convert supplied expression")



