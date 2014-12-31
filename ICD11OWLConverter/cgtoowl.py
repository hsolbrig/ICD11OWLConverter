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

import sys
import argparse
import re
import io
from rdflib import Graph, URIRef, ConjunctiveGraph

from ConverterGateway import SCTConverterGateway
from namespaces import namespaces

# This is the annotation property that carries the compositional grammar definition
icdf_comments = URIRef(namespaces['icdf'] + "Description.entity.en.Comments")

# CG definitions may include reference url/s following
cgre1 = re.compile(r'.*Expression (\(pre-coordinated\)|\(post_coordinated\))\s*(.*?)http(s?)://.*$')
cgre2 = re.compile(r'.*Expression (\(pre-coordinated\)|\(post_coordinated\))\s*(.*)')

# Expressions of lines to remove for remove sctid
remove_list = [re.compile(r'^<' + namespaces['sctid'] + r'\d+> rdfs:label .*\.'),
               re.compile(r'^<' + namespaces['sctid'] + r'\d+> a owl:Class \.$'),
               re.compile(r'^<' + namespaces['sctid'] + r'\d+> a owl:ObjectProperty \.$')]

# The SCTConverter builds an illegal base expression.  This fixes this
owlbasere = re.compile(r'(^@base <.*)#>', flags=re.MULTILINE)


def fix_prefixes(owltext):
    """ Change the prefixes in a text file to the local namespace form
    :param owltext: text to change
    :return: text with prefixes mapped
    """
    # This could be simplified if we could figure out how to get negative look-aheads to work...
    def fix_prefix(l):
        for k, v in namespaces.items():
            l = re.sub('<' + str(v) + r'(.*?)>', k + r':\1', l, flags=re.DOTALL)
        return l
    return '\n'.join([l if l.startswith('@prefix') else fix_prefix(l) for l in owltext.split('\n')])

def add_namespaces(g):
    list(g.bind(k, v) for k, v in namespaces.items())
    return g

def map_namespace(subj):
    if ':' in subj and not '//' in subj:
        ns, n = subj.split(':', 1)
        if ns in namespaces:
            return namespaces[ns] + n
        return subj
    # Default is who
    if re.match(r'^\d+$', subj):
        return namespaces['who'] + subj
    return subj

def parse_and_load(gw, subj, primitive, cgexpr, g):
    """ Parse the conceptual grammar expression for the supplied subject and, if successful, add
    it to graph g.
    :param gw: parser gateway
    :param subj: subject of expression
    :param primitive: true means subClassOf, false means equivalentClass
    :param cgexpr: expression to parse
    :param g: graph to add the result to
    :return: true means success, false error
    """
    ttlresult = gw.parse(subj, primitive, cgexpr)
    if ttlresult:
        ttlresult = owlbasere.sub(r'\1>', ttlresult)
        g.parse(io.StringIO(ttlresult), format='n3')
    return bool(ttlresult)

def serialize_graph(g, format="turtle", removesctid=False, shorturi=False):
    try:
        target = g.serialize(format="turtle").decode('utf-8')
    except Exception as e:
        return None, (400, e)
    if removesctid:
        target = ('\n'.join([l for l in target.split('\n') if not any(e.match(l) for e in remove_list)])).strip()
    if shorturi:
        target = fix_prefixes(target)
    out_g = ConjunctiveGraph()
    out_g.parse(io.StringIO(target), format="turtle")
    try:
        target = out_g.serialize(format=format).decode('utf-8')
    except Exception as e:
        return None, (400, e)
    return target


def main(args):
    """ Extract the Compositional Grammar expressions from an OWL file and convert them into an offical importable OWL
    file
    """

    optparser = argparse.ArgumentParser(description="Generate OWL from Comments in an ICD-11 file")
    optparser.add_argument('owlfile', help="Input OWL file")
    optparser.add_argument('-f', '--fullydefined', help="Definitions are fully defined", action="store_true")
    optparser.add_argument('-p', '--port', help="SCT Converter gateway port", type=int)
    optparser.add_argument('-o', '--out', help="Output file", required=True)
    optparser.add_argument('-s', '--shorturi', help="Shorten URI's for readability", action="store_true")
    optparser.add_argument('-r', '--removesctid', help="Remove the SCT class declarations", action="store_true")

    opts = optparser.parse_args(args)

    gw = SCTConverterGateway(opts.port) if opts.port else SCTConverterGateway()

    g = Graph()
    target_graph = add_namespaces(Graph())
    g.parse(opts.owlfile)
    target_graph.parse(opts.owlfile)

    # Iterate over the comments with the compositional expressions
    for subj, desc in list(g.subject_objects(icdf_comments)):
        if cgre1.search(desc):
            cgexpr = cgre1.sub(r'\2', desc)
        elif cgre2.search(desc):
            cgexpr = cgre2.sub(r'\2', desc)
        else:
            cgexpr = None

        if cgexpr:
            if not parse_and_load(gw, subj, not bool(opts.fullydefined), cgexpr, target_graph):
                print("Conversion error on %s (%s)" % (subj, cgexpr), file=sys.stderr)
        else:
            print("No conversion available for %s (%s)" % (subj, desc), file=sys.stderr)
    target = serialize_graph(target_graph, removesctid=opts.removesctid, shorturi=opts.shorturi)
    open(opts.out, 'w').write(target)


if __name__ == '__main__':
    main(sys.argv[1:])
