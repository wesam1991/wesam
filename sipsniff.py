#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Jose Luis Verdeguer'
__version__ = '3.1.1'
__license__ = "GPL"
__copyright__ = "Copyright (C) 2015-2022, SIPPTS"
__email__ = "pepeluxx@gmail.com"

from modules.sipsniff import SipSniff
from lib.params import get_sniff_args


def main():
    dev, ofile, auth, verbose, proto = get_sniff_args()

    s = SipSniff()
    s.dev = dev
    s.ofile = ofile
    s.auth = auth
    s.verbose = verbose
    s.proto = proto

    s.start()


if __name__ == '__main__':
    main()
