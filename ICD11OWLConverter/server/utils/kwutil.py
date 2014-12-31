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


import collections
from functools import reduce


def kwget(args, dicts, op=lambda x: x, default=None, ignorecase=True):
    """ Function to pull a list of arguments from an ordered list of dictionaries.

    @param args: a key or ordered list of keys for the desired value in C{dicts}
    @param dicts: a dictionary or list of dictionaries to look for the keys in
    @param op: an operation to apply to the matched value before return.  Default: identity function
    @param default: the default value if no match is located
    @param ignorecase: True means ignore case on arguments, False means pay attention
    @return: op(dict[key])

    Example use:
        >>> kwget(['lang', 'referenceLanguage', 'refLang', 'Accept-Language'],
        ...       [{'referencelanguage':'en','maxtoreturn':10}, {'Accept-Language' : 'da, en-gb;q=0.8, en;q=0.7'}],
        ...        preference_order,
        ...        'en')
        ['en']
        >>> kwget(['lang', 'referenceLanguage', 'refLang', 'Accept-Language'],
        ...       {'Accept-Language' : 'da, en-gb;q=0.8, en;q=0.7'},
        ...       preference_order,
        ...       'en')
        ['da', 'en-gb', 'en']
    """
    if isinstance(args, str) or not isinstance(args, collections.Iterable):
        args = [args]
    if not isinstance(dicts, (list, tuple)):
        dicts = [dicts]
    for d in dicts:
        dc = {k.lower(): d for k, d in d.items()} if ignorecase else d
        for a in args:
            ac = a.lower() if ignorecase else a
            if ac in dc:
                return op(dc[ac])
    return op(default)


def preference_order(httpstr):
    """ Parse an HTTP string in preference order

    @param httpstr: preference order field
    @return: list of targets in descending order of preference
    """
    return [e[0].strip() for e in
            filter(lambda e: e[0], [e for e in
                                    sorted([(x[0], float(x[1]) if len(x) > 1 else 1.0) for x in
                                            [e.split(';q=') for e in httpstr.split(',')]],
                                           key=lambda e: e[1],
                                           reverse=True)])]


def best_match(match_list, request_list):
    """
    @param match_list: Ordered list of available entries
    @param request_list: Ordered list of requested entries
    @return: first entry in the request list that is available in the match list

    Based on U{http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html}, we search in the following order:
    1. Find an exact match

    2. If the match field has a semicolon in it, truncate it and look for an exact match on anything without
       an asterisk

    3. Look for a match on 'x/*'
    4. Look for */*
    """
    ordered_request_list = {k: v for k, v in zip(request_list, range(0, len(request_list)))}
    matches = {}  # Map from key to request_order / rule order (for tie breaker)
    # exact match
    for m in match_list:
        if m in ordered_request_list:
            matches[m] = (ordered_request_list[m], 0)
    # match up to ';'
    for m in match_list:
        if m not in matches and ';' in m:
            mp = m[0:m.index(';')]
            if mp in ordered_request_list:
                matches[m] = (ordered_request_list[mp], 1)
    # x/* match
    for m in match_list:
        if m not in matches and '/' in m:
            mp = m[0:m.index('/') + 1] + '*'
            if mp in ordered_request_list:
                matches[m] = (ordered_request_list[mp], 2)
    # */* match
    if '*/*' in ordered_request_list:
        for m in match_list:
            if m not in matches:
                matches[m] = (ordered_request_list['*/*'], 3)
                break
    if len(matches):
        return reduce(lambda k1, k2: k1 if k1[1] <= k2[1] else k2, matches.items())[0]
    return None
