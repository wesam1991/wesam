#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Jose Luis Verdeguer'
__version__ = '3.1.1'
__license__ = "GPL"
__copyright__ = "Copyright (C) 2015-2022, SIPPTS"
__email__ = "pepeluxx@gmail.com"

from modules.rtpbleed import RTPBleed
from lib.params import get_rtpbleed_args


def main():
    ip, start_port, end_port, loops, payload, delay = get_rtpbleed_args()

    s = RTPBleed()
    s.ip = ip
    s.start_port = start_port
    s.end_port = end_port
    s.loops = loops
    s.payload = payload
    s.delay = delay

    s.start()


if __name__ == '__main__':
    main()
