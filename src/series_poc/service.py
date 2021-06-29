#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""
:mod:`series_poc.service` -- series service
"""
import logging
import tornado.web as tw
import tornado.ioloop as ti

from dbc_pyutils import JSONFormatter
from dbc_pyutils import build_info
from dbc_pyutils import create_instance_id
from dbc_pyutils import Statistics
from dbc_pyutils import Stat
from dbc_pyutils import BaseHandler
from dbc_pyutils import StatusHandler
from dbc_pyutils import StaticHandler
from dbc_pyutils import create_post_examples_from_dir

logger = logging.getLogger(__name__)

STAT = Statistics(name='series_poc')
INSTANCE_ID = create_instance_id(num_digits=8)


class MainHandler(BaseHandler):
    """ Main Handler """
    def initialize(self, stat_collector):
        self.stat_collector = stat_collector

    async def get(self):
        with Stat(self.stat_collector):
            self.write("Series POC!")



def make_app(ab_id):

    info = build_info.get_info('series_poc')
    handlers = [(r"/", MainHandler, {'stat_collector': STAT}),
                (r"/status", StatusHandler, {'ab_id': ab_id,
                                             'info': info,
                                             'statistics': [STAT],
                                             'instance_id': INSTANCE_ID})]
    return tw.Application(handlers)


def main(port, ab_id):

    app = make_app(ab_id)
    logger.info("service up at port %d", port)
    app.listen(port)
    ti.IOLoop.current().start()


def cli():
    """ Commandline interface """
    import argparse

    port = 5000

    parser = argparse.ArgumentParser(description='series service')
    parser.add_argument('-a', '--ab-id', dest='ab_id',
                        help="ab id of service. default is 1", default=1)
    parser.add_argument('-p', '--port', dest='port', type=int,
                        help='port to expose service on. Default is %d' % port, default=port)
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='verbose output')
    args = parser.parse_args()

    structured_formatter = JSONFormatter(instance_id=INSTANCE_ID, tags={'type': 'service', 'port': args.port})
    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG

    logger = logging.getLogger('')
    ch = logging.StreamHandler()
    ch.setFormatter(structured_formatter)
    ch.setLevel(level)
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)
    main(args.port, args.ab_id)

