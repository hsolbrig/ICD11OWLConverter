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
from os import listdir, remove
from os.path import join
import re
import unittest

from ICD11OWLConverter import cgtoowl


class TestCGToOWL(unittest.TestCase):
    def setUp(self):
        self._tmpf = join(sys.path[0], 'tmp')

    def test_files(self):
        data = join(sys.path[0], '..', 'data')
        for f in listdir(data):
            if re.match(('test.*_in\.'), f):
                inf = join(data, f)
                outf = join(data, f.replace('_in.', '_out.'))
                cgtoowl.main([inf, '-o' + self._tmpf])
                self.assertEqual(open(outf).read(), open(self._tmpf).read())
                outf = join(data, f.replace('_in.', '_out_f.'))
                cgtoowl.main([inf, '-o' + self._tmpf, '-f'])
                self.assertEqual(open(outf).read(), open(self._tmpf).read())
                outf = join(data, f.replace('_in.', '_out_s.'))
                cgtoowl.main([inf, '-o' + self._tmpf, '-s'])
                self.assertEqual(open(outf).read(), open(self._tmpf).read())
                outf = join(data, f.replace('_in.', '_out_r.'))
                cgtoowl.main([inf, '-o' + self._tmpf, '-r'])
                self.assertEqual(open(outf).read(), open(self._tmpf).read())
                outf = join(data, f.replace('_in.', '_out_rs.'))
                cgtoowl.main([inf, '-o' + self._tmpf, '-r', '-s'])
                self.assertEqual(open(outf).read(), open(self._tmpf).read())
                remove(self._tmpf)

                



if __name__ == '__main__':
    unittest.main()
