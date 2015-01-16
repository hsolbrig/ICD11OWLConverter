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
from rdflib import Graph, OWL, RDFS, Literal

from ICD11OWLConverter.namespaces import namespaces
from ontology_defs import map_ontology


def main(args):
    """ Create two files from the input file.  One with the ICD declarations and
    a second with the equivalent and subclass declarations
    """
    optparser = argparse.ArgumentParser(description="Split the input file into two output files -- one with pure ICD and a second with maps")
    optparser.add_argument('owlfile', help="Input OWL file")
    optparser.add_argument('-f', '--format', help="File format", default="n3")
    optparser.add_argument('-of', '--outformat', help="Output file format(default is same as input)")

    opts = optparser.parse_args(args)
    if not opts.outformat:
        opts.outformat = opts.format

    g = Graph()
    print("Reading " + opts.owlfile)
    g.parse(opts.owlfile, format=opts.format)
    map_g = Graph()
    list(map_g.bind(ns[0], ns[1]) for ns in g.namespaces() if ns[0])
    list(map_g.add(e) for e in map_ontology)

    # Iterate over the assertions
    strwho = str(namespaces['who'])
    strsct = str(namespaces['sctid'])
    for s, o in g[:OWL.equivalentClass]:
        # TODO: find the official way of determining namespaces
        if (str(s).startswith(strwho) and str(o).startswith(strsct)) or \
                (str(s).startswith(strsct) and str(o).startswith(strwho)):
            map_g.add((s, OWL.equivalentClass, o))
            g.remove((s, OWL.equivalentClass, o))

    whostr = str(namespaces['who'])
    for s, o in list(g[:RDFS.label]):
        if str(s).startswith(whostr):
            g.add((s, RDFS.label, Literal('ICD  ' + str(o))))
            g.remove((s, RDFS.label, o))

    open(opts.owlfile + 'nomaps.ttl', 'wb').write(g.serialize(format=opts.outformat))
    print(opts.owlfile + 'nomaps.ttl written')
    open(opts.owlfile + 'maps.ttl', 'wb').write(map_g.serialize(format=opts.outformat))
    print(opts.owlfile + 'maps.ttl written')


if __name__ == '__main__':
    main(sys.argv[1:])
