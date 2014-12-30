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
from rdflib import Graph, URIRef
from functools import reduce

from ConverterGateway import SCTConverterGateway

# This is the annotation property that carries the compositional grammar definition
icdf_comments = URIRef("http://who.int/field/Description.entity.en.Comments")

# CG definitions may include reference url/s following
cgre1 = re.compile(r'.*Expression (\(pre-coordinated\)|\(post_coordinated\))\s*(.*?)http(s?)://.*$')
cgre2 = re.compile(r'.*Expression (\(pre-coordinated\)|\(post_coordinated\))\s*(.*)')

# The SCTConverter builds an illegal base expression.  This fixes this
owlbasere = re.compile(r'(^@base <.*)#>', flags=re.MULTILINE)

# Prefix cleaner upperer -- see conversionbase.owl for prefixes
prefixmaps = [(r'<http://snomed.info/id/(.*?)>', r'sctid:\1'),
              (r'<http://id.who.int/icd/entity/(.*?)>', r'who:\1')]


def fix_prefixes(owltext):
    """ Change the prefixes in a text file to the local namespace form
    :param owltext: text to change
    :return: text with prefixes mapped
    """
    # This could be simplified if we could figure out how to get negative look-aheads to work...
    def fix_prefix(l):
        return reduce(lambda text, e: re.sub(e[0], e[1], text, flags=re.DOTALL), prefixmaps, l)
    return '\n'.join([l if l.startswith('@prefix') else fix_prefix(l) for l in owltext.split('\n')])


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

    opts = optparser.parse_args(args)

    gw = SCTConverterGateway(opts.port) if opts.port else SCTConverterGateway()

    g = Graph()
    target_graph = Graph()
    g.parse(opts.owlfile)
    list(target_graph.add(t) for t in g.triples((None, None, None)))
    # target_graph.parse('../data/conversionbase.owl', format='n3')

    # Iterate over the comments with the compositional expressions
    for subj, desc in list(g.subject_objects(icdf_comments)):
        if cgre1.search(desc):
            cgexpr = cgre1.sub(r'\2', desc)
        elif cgre2.search(desc):
            cgexpr = cgre2.sub(r'\2', desc)
        else:
            cgexpr = None

        if cgexpr:
            # Convert the expressions into turtle
            ttlresult = gw.parse(subj, not bool(opts.fullydefined), cgexpr)
            if ttlresult:
                ttlresult = owlbasere.sub(r'\1>', ttlresult)
                target_graph.parse(io.StringIO(ttlresult), format='n3')
            else:
                print("Conversion error on %s (%s)" % (subj, cgexpr), file=sys.stderr)
        else:
            print("No conversion available for %s (%s)" % (subj, desc), file=sys.stderr)

    target = target_graph.serialize(format='turtle').decode('utf-8')
    if opts.shorturi:
        target = fix_prefixes(target)
    open(opts.out, 'w').write(target)


if __name__ == '__main__':
    main(sys.argv[1:])
