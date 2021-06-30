#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""
:mod:`series_poc.service` -- series service
"""
import json
import logging
import os
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
from dbc_data import lowell_mapping_functions as lmf
from dataclasses import dataclass
from dataclasses import field
from typing import Type

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

@dataclass
class Series:
    series_title: str
    series_description: str
    related_series: str
    number_in_universe: int
    universe: Type["Universe"]
    included_works: set[str] = field(default_factory=set)

@dataclass
class Work:
    workid: str
    series: Type["Series"]
    number_in_series: int
    can_be_read_independently: bool
    universe: Type["Universe"]

@dataclass
class Universe:
    universe_title: str
    universe_description: str
    universe_alternative_title: str
    included_series: set[str] = field(default_factory=set)
    included_works: set[str] = field(default_factory=set)

class DataProvider:
    works_dict: dict[str, Work] = {}
    series_dict: dict[str, Series] = {}
    universe_dict: dict[str, Universe] = {}

    def __init__(self, works_dict: dict[str, Work], series_dict: dict[str, Series], universe_dict: dict[str, Universe], pid2metadata: dict) -> None:
        self.works_dict = works_dict
        self.series_dict = series_dict
        self.universe_dict = universe_dict
        self.pid2metadata = pid2metadata
    
    def get_pid_info(self, pid: str):
        work : Work = self.works_dict.get(pid, None) 
        return {
            "work_id": work.workid,
            "work_metadata": self.pid2metadata.get(work.workid, ""),
            "series_title": work.series.series_title,
            "universe_title": work.universe.universe_title
        }

    def get_series_info(self, series_title: str):
        series : Series = self.series_dict.get(series_title, None)
        return {
            "title": series.series_title,
            "description": series.series_description,
            "related_series": series.related_series,
            "number_in_universe": series.number_in_universe,
            "universe_title": series.universe.universe_title,
            "pids": list(series.included_works)
        }

    def get_universe_info(self, universe_title: str):
        universe = self.universe_dict.get(universe_title, None)
        return {
            "title": universe.universe_title,
            "description": universe.universe_description,
            "alternative_title": universe.universe_alternative_title,
            "included_series": list(universe.included_series),
            "included_works": list(universe.included_works)
        }

class SeriesHandler(BaseHandler):
    def initialize(self, data_provider: DataProvider, stat_collector):
        self.stat_collector = stat_collector
        self.data_provider = data_provider

    def get(self):
        series_title = self.get_argument("title")
        logger.info(f"series endpoint called with argument {series_title}")
        res = self.data_provider.get_series_info(series_title)
        self.write(res)
    

class UniverseHandler(BaseHandler):
    def initialize(self, data_provider, stat_collector):
        self.stat_collector = stat_collector
        self.data_provider = data_provider

    def get(self):
        universe_title = self.get_argument("title")
        logger.info(f"universe endpoint called with argument {universe_title}")
        res = self.data_provider.get_universe_info(universe_title)
        self.write(res)

class WorkHandler(BaseHandler):
    def initialize(self, data_provider, stat_collector):
        self.stat_collector = stat_collector
        self.data_provider = data_provider

    def get(self):
        work_id = self.get_argument("workid")
        logger.info(f"pid called with argument {work_id}")
        res = self.data_provider.get_pid_info(work_id)
        self.write(res)


def make_app(ab_id, data_provider: DataProvider):
    info = build_info.get_info('series_poc')
    handlers = [(r"/", MainHandler, {'stat_collector': STAT}),
                (r"/status", StatusHandler, {'ab_id': ab_id,
                                             'info': info,
                                             'statistics': [STAT],
                                             'instance_id': INSTANCE_ID}),
                (r"/universe", UniverseHandler, {'data_provider': data_provider, 'stat_collector': STAT}),
                (r"/series", SeriesHandler, {'data_provider': data_provider, 'stat_collector': STAT}),
                (r"/pid", WorkHandler, {'data_provider': data_provider, 'stat_collector': STAT})
            ]
    return tw.Application(handlers)

def main(args):
    port = args.port
    ab_id = args.ab_id
    data_dir = args.data_dir
    works_dict: dict[str, Work] = {}
    series_dict: dict[str, Series] = {}
    universe_dict: dict[str, Universe] = {}
    if data_dir:
        logger.info(f"Reading data files from {data_dir}")
        json_files = [json_file for json_file in os.listdir(data_dir) if json_file.endswith('.json')]
        for jf in json_files:
            works_dict, series_dict, universe_dict = read_json_file(data_dir, jf, works_dict, series_dict, universe_dict)
    pid2metadata = lmf.pid2metadata (works_dict.keys())
    data_provider = DataProvider(works_dict, series_dict, universe_dict, pid2metadata)
    app = make_app(ab_id, data_provider)

    logger.info(f"service up at port {port}")
    app.listen(port)
    ti.IOLoop.current().start()

def read_json_file(path, filename, input_works_dict, input_series_dict, input_universe_dict):
    works_dict: dict[str, Work] = input_works_dict
    series_dict: dict[str, Series] = input_series_dict
    universe_dict: dict[str, Universe] = input_universe_dict
    logger.info(f"reading json file {filename} in {path}")
    with open(os.path.join(path, filename)) as fp:
        obj_list = json.load(fp)
        logger.info("reading universes info...")
        for obj in obj_list:
            if "universeTitle" in obj and not obj["universeTitle"] in universe_dict:
                universe_description = obj.get("universeDescription", None)
                universe_alternative_title = obj.get("universeAlternativeTitle", None)
                universe = Universe(universe_title=obj["universeTitle"], universe_description=universe_description, universe_alternative_title=universe_alternative_title)
                universe_dict[obj["universeTitle"]] = universe
        logger.info("reading series info...")
        for obj in obj_list:
            if "seriesTitle" in obj and not obj["seriesTitle"] in series_dict:
                series_descr = obj.get("seriesDescription", None)
                number_in_universe_str = obj.get("numberInUniverse", None)
                number_in_universe = int(number_in_universe_str) if number_in_universe_str  else None
                related_series = obj.get("relatedSeries", None)
                universe = universe_dict[obj["universeTitle"]] if "universeTitle" in obj else None
                series = Series(series_title=obj["seriesTitle"], series_description=series_descr, related_series=related_series, number_in_universe=number_in_universe, universe=universe)
                series_dict[obj["seriesTitle"]] = series
                if universe:
                    universe.included_series.add(series.series_title)
        logger.info("reading works info...")
        for obj in obj_list:
            if "workId" in obj and not obj["workId"] in works_dict:
                series = series_dict.get(obj["seriesTitle"], None) if "seriesTitle" in obj else None
                number_in_series_str = obj.get("numberInSeries", None)
                number_in_series = int(number_in_series_str) if number_in_series_str else None
                can_be_read_independently = obj.get("canBeReadIndependently", False)
                universe = universe_dict.get(obj["universeTitle"], None) if "universeTitle" in obj else None
                work = Work(workid=obj["workId"], series=series, number_in_series=number_in_series, can_be_read_independently=can_be_read_independently, universe=universe)
                works_dict[obj["workId"]] = work
                if series:
                    series.included_works.add(work.workid)
                if universe:
                    universe.included_works.add(work.workid)
    return works_dict, series_dict, universe_dict


def cli():
    """ Commandline interface """
    import argparse

    port = 5000

    parser = argparse.ArgumentParser(description='series service')
    parser.add_argument('-a', '--ab-id', dest='ab_id',
                        help="ab id of service. default is 1", default=1)
    parser.add_argument('-p', '--port', dest='port', type=int,
                        help=f"port to expose service on. Default is {port}", default=port)
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='verbose output')
    parser.add_argument('-d', '--data-dir', dest='data_dir', help='dir containing series json data files', default="data-files/")
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
    main(args)

