#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re
from logging import debug
import requests
import hashlib
import requests
from argparse import ArgumentParser
from cStringIO import StringIO
from lxml import etree, html
from jsparser import parse

PASSWORD = '***'
FRITZBOXURL = 'http://fritz.box'

def login ():
    debug ("login ()")
    login = requests.get (FRITZBOXURL + '/login.lua')
    for line in login.text.split ('\n'):
        mo = re.match (r'g_challenge = \"(?P<challenge>\w+)\"', line)
        if not mo is None:
            break
    if not mo is None:
        challenge = mo.groupdict ()['challenge']
    else:
        critical ("challenge not found")
    debug ("challenge: %s", challenge)
    md5 = hashlib.md5 ()
    md5.update (challenge.encode ('utf-16le'))
    md5.update ('-'.encode ('utf-16le'))
    md5.update (PASSWORD.encode ('utf-16le'))
    response = challenge + '-' + md5.hexdigest ()
    debug ("response: %s", response)
    login = requests.get (FRITZBOXURL + '/login.lua', params = { 'response': response })
    debug ("url: %s", login.url)
    for line in login.text.split ('\n'):
        mo = re.match (r'.*sid=(?P<sid>[0-9a-f]*)', line)
        if not mo is None:
            break
    if not mo is None:
        sid = mo.groupdict ()['sid']
    else:
        critical ("sid not found")
    return sid

def get_rufumleitung (sid):
    debug ("get_rufumleitung (%s)", sid)
    r = requests.get (FRITZBOXURL + '/fon_num/rul_list.lua', params = { 'sid': sid })
    return html.parse (StringIO (r.text.encode (r.encoding)))

def set_rufumleitung (sid, rufumleitungs):
    debug ("set_rufumleitung (%s, %s)", sid, rufumleitungs)
    payload = { 'apply': '', 'back_to_page': '/fon_num/rul_list.lua', 'sid': sid }
    for ru in rufumleitungs:
        payload ['rul_%s' % ru] = 'on'
    r = requests.post (FRITZBOXURL + '/fon_num/rul_list.lua', data = payload)
    return html.parse (StringIO (r.text.encode (r.encoding)))

def eval_html (tree):
    debug ("eval_html ()")
    g_RulList = []
    for child in tree.xpath ('//script'):
        # find script without src
        if child.attrib.get ('src') is None:
            # parse javascript
            p = parse (child.text.encode ('utf-8'))
            # find var g_RulList
            for varDec in p.varDecls:
                if varDec.name == 'g_RulList':
                    for initializer in varDec.initializer:
                        tmp = {}
                        for init in initializer:
                            tmp [init [0].value] = init [1].value 
                        g_RulList.append (tmp)
#   debug ("g_RulList: %s", g_RulList)
    return g_RulList

def show (g_RulList):
    fields = [('idx', 3), ('num_dest', -15), ('active', -6), ('type', -3)]
    for name, width in fields:
        print "%*s" % (width, name),
    print
    for rule in g_RulList:
        for name, width in fields:
            print "%*s" % (width, rule [name]),
        print

def run ():
    parser = ArgumentParser ()
    parser.add_argument ('-l', '--logging',
                         help = 'log_level (DEBUG|INFO|WARNING|ERROR|CRITICAL)',
                         dest = 'log_level')
    parser.add_argument ('-r', '--rufumleitung',
                         help = 'Rufumleitung-Indices',
                         dest = 'rufumleitungs',
                         nargs = '*',
                         type = int,
                         action = 'append',
                        )
    args = parser.parse_args ()
    if not args.log_level is None:
        logging.basicConfig(level = args.log_level.upper())
    sid = login ()
    tree = get_rufumleitung (sid)
    g_RulList = eval_html (tree)
    if not args.rufumleitungs is None:
        rufumleitungs = [a [0] for a in filter (lambda a: len (a) > 0, args.rufumleitungs)]
        tree = set_rufumleitung (sid, rufumleitungs)
        g_RulList = eval_html (tree)
    show (g_RulList)

if __name__ == '__main__':
    run ()
