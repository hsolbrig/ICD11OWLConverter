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
import csv
import sys
import argparse
import re
from rdflib import Graph, URIRef, RDF, RDFS, OWL, Literal
from io import StringIO

from namespaces import namespaces, ICDCG, WHO, SCTCG
from ConverterGateway import SCTConverterGateway
from ontology_defs import cg_ontology




# maptype values.  post_coordinated means that the definition is the responsibility of the WHO
#                  pre_coordinated means it is the responsibility of IHTSDO
post_coordinated = 'A'
pre_coordinated = 'E'

# signature of a single concept
single_concept_re = re.compile(r'\s*\d+\s*\|[^|]+\|\s*$')

# The SCTConverter builds an illegal base expression.  This fixes this
owlbasere = re.compile(r'(^@base <.*)#>', flags=re.MULTILINE)


def init_graph():
    g = Graph()
    list(g.bind(ns, uri) for ns, uri in namespaces.items())
    list(g.add(t) for t in cg_ontology)
    return g

strsct = str(namespaces['sctid'])
def rem_sct_labels(g):
    for s, o in list(g[:RDFS.label]):
        if str(s).startswith(strsct):
            g.remove((s, RDFS.label, o))


def main(args):
    """ Convert a TSV file with the following columns:
    * icd11 - the URI of the ICD 11 resource
    * icdrubric - the name associated with the rubric
    * expression - a compositional grammar expression that fully or partially defines the ICD 11 resource
    * maptype - "A" means the definition belongs to WHO, "E" means it belongs to IHTSDO (and should be added to SNOMED CT)
    """
    optparser = argparse.ArgumentParser(description="Convert cardio raw expressions into OWL")
    optparser.add_argument('infile', help="Input tab separated value file file")
    optparser.add_argument('-f', '--outputformat', help="File format", default="n3")
    optparser.add_argument('-p', '--port', help="SCT Converter gateway port", type=int)
    optparser.add_argument('-o', '--outfile', help="Output file name", required=True)
    optparser.add_argument('-m', '--mapfile', help="Map file name")

    opts = optparser.parse_args(args)

    gw = SCTConverterGateway(opts.port) if opts.port else SCTConverterGateway()
    cg_graph = init_graph()
    map_graph = Graph().parse(opts.mapfile, format='n3') if opts.mapfile else None
    with open(opts.infile) as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        for row in reader:
            who_entity = row['icd11'].split(str(WHO))[1]
            subj = URIRef(str(ICDCG if row['maptype'] == post_coordinated else SCTCG) + who_entity)
            primitive = bool(single_concept_re.match(row['expression']))
            ttlresult = gw.parse(subj, primitive, row['expression'])
            if ttlresult:
                cg_graph.parse(StringIO(owlbasere.sub(r'\1>', ttlresult)), format='n3')
                cg_graph.add( (subj, RDFS.label, Literal('ICDCG  ' + row['icdrubric'])))
                if map_graph:
                    owlc = URIRef(str(WHO) + who_entity)
                    map_graph.add( (owlc, OWL.equivalentClass, subj))
            else:
                print("Conversion failure: " + str(row))

        rem_sct_labels(cg_graph)
        cg_graph.serialize(opts.outfile, format="n3")
        print("OWL saved to %s" % opts.outfile)
        if map_graph:
            map_graph.serialize(opts.mapfile + 'upd.ttl', format="n3")
            print("Map saved to %s" % opts.mapfile + 'upd.ttl')


if __name__ == '__main__':
    main(sys.argv[1:])