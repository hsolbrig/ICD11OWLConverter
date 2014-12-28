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
from rdflib import Graph, RDFS, Literal



def main(args):
    """ Rewrite an OWL file adding a prefix to the label
    """

    optparser = argparse.ArgumentParser(description="Add a tag prefix to the labels in the supplied owl file")
    optparser.add_argument('owlfile', help="Input OWL file")
    optparser.add_argument('-t', '--tag', help="Tag to prefix", required=True)
    optparser.add_argument('-f', '--format', help="Input format", default="xml")

    opts = optparser.parse_args(args)

    g = Graph()
    g.parse(opts.owlfile, format=opts.format)

    # Iterate over the labels
    for subj, desc in list(g.subject_objects(RDFS.label)):
        g.remove([subj, RDFS.label, desc])
        g.add([subj, RDFS.label, Literal(opts.tag + str(desc))])
    g.serialize(opts.owlfile+".ttl", format="n3")


if __name__ == '__main__':
    main(sys.argv[1:])
