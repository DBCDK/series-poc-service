#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""
:mod:`series_poc.service` -- series service
"""
import logging
import os
import typing
import tornado.web as tw
import tornado.ioloop as ti
from dbc_pyutils import JSONFormatter
from dbc_pyutils import build_info
from dbc_pyutils import create_instance_id
from dbc_pyutils import Statistics
from dbc_pyutils import Stat
from dbc_pyutils import BaseHandler
from dbc_pyutils import StatusHandler
from dbc_data import lowell_mapping_functions as lmf
from dataclasses import dataclass
from dataclasses import field
from typing import Type
import json5

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
class Work:
    workid: str
    can_be_read_independently: bool
    universe: Type["Universe"]
    series_memberships: typing.Dict[str, typing.List[float]] = field(default_factory=dict) # dict from str (series titles) -> list[str] - latter str can be like '7.2'

@dataclass
class Series:
    series_title: str
    series_description: str
    number_in_universe: int
    universe: Type["Universe"]
    included_works: typing.Set[str] = field(default_factory=set) # set of WorkIds
    series_alternative_title: typing.List[str] = field(default_factory=list) # list of strings

@dataclass
class Universe:
    universe_title: str
    universe_description: str
    universe_alternative_title: typing.List[str] = field(default_factory=list) # list of strings
    included_series: typing.Set[str] = field(default_factory=set) # set of series titles (strings) 
    included_works: typing.Set[str] = field(default_factory=set) # set of workIds (strings)

class DataProvider:

    def __init__(self, works_dict: dict, series_dict: dict, universe_dict: dict, pid2metadata: dict) -> None:
        self.works_dict = works_dict
        self.series_dict = series_dict
        self.universe_dict = universe_dict
        self.pid2metadata = pid2metadata
        self.series_works_dict = {}
    
    def get_pid_info(self, pid: str):
        work : Work = self.works_dict.get(pid, None) 
        if not work:
            return {}
        res = {
            "work_id": work.workid,
            "work_metadata": self.pid2metadata.get(work.workid, "")
        }
        if work.series_memberships:
            res["series_memberships"] = [{self.series_dict[key].series_title: work.series_memberships[key]} for key in work.series_memberships]
        if work.universe:
            res["universe_title"] = work.universe.universe_title
        return res
    
    def get_all_works(self):
        return {"works": list(self.works_dict.keys())}

    def get_series_info(self, series_title: str):
        series : Series = self.series_dict.get(series_title, None)
        if not series:
            return {}
        res = {
            "title": series.series_title,
            "description": series.series_description
        }
        if not series_title in self.series_works_dict:
            self.series_works_dict[series_title] = sorted(list(series.included_works), key=lambda workid: series_num(workid=workid, works_dict=self.works_dict, series_title=series.series_title))
        res["pids"] = self.series_works_dict[series_title]
        if series.series_alternative_title and len(series.series_alternative_title) > 0:
            res["alternative_title"] = series.series_alternative_title
        if series.universe:
            res["universe_title"] = series.universe.universe_title
        if series.number_in_universe:
            res["number_in_universe"] = series.number_in_universe
        return res

    def get_all_series(self):
        return {"series": sorted(list(self.series_dict.keys()))}

    def get_universe_info(self, universe_title: str):
        universe = self.universe_dict.get(universe_title, None)
        res = {
            "title": universe.universe_title,
            "description": universe.universe_description,
            "included_series": list(universe.included_series),
            "included_works": list(universe.included_works)
        }
        if universe.universe_alternative_title:
            res["alternative_title"] = universe.universe_alternative_title
        return res
    
    def get_all_universes(self):
        return {"universes": sorted(list(self.universe_dict.keys()))}

class SeriesHandler(BaseHandler):
    def initialize(self, data_provider: DataProvider, stat_collector):
        self.stat_collector = stat_collector
        self.data_provider = data_provider

    def get(self):
        series_title = self.get_argument("title")
        logger.info(f"series endpoint called with argument {series_title}")
        res = self.data_provider.get_series_info(series_title)
        if res:
            self.write(res)
        else:
            self.set_status(404)
    
class SeriesAllHandler(BaseHandler):
    def initialize(self, data_provider: DataProvider, stat_collector):
        self.stat_collector = stat_collector
        self.data_provider = data_provider

    def get(self):
        logger.info(f"series-all endpoint called")
        res = self.data_provider.get_all_series()
        self.write(res)
    

class UniverseHandler(BaseHandler):
    def initialize(self, data_provider, stat_collector):
        self.stat_collector = stat_collector
        self.data_provider = data_provider

    def get(self):
        universe_title = self.get_argument("title")
        logger.info(f"universe endpoint called with argument {universe_title}")
        res = self.data_provider.get_universe_info(universe_title)
        if res:
            self.write(res)
        else:
            self.set_status(404)

class UniversesAllHandler(BaseHandler):
    def initialize(self, data_provider: DataProvider, stat_collector):
        self.stat_collector = stat_collector
        self.data_provider = data_provider

    def get(self):
        logger.info(f"universe-all endpoint called")
        res = self.data_provider.get_all_universes()
        if res: 
            self.write(res)
        else:
            self.set_status(404)
    
class WorkHandler(BaseHandler):
    def initialize(self, data_provider, stat_collector):
        self.stat_collector = stat_collector
        self.data_provider = data_provider

    def get(self):
        work_id = self.get_argument("workid")
        logger.info(f"pid called with argument {work_id}")
        res = self.data_provider.get_pid_info(work_id)
        if res:
            self.write(res)
        else:
            self.set_status(404)

class WorkAllHandler(BaseHandler):
    def initialize(self, data_provider: DataProvider, stat_collector):
        self.stat_collector = stat_collector
        self.data_provider = data_provider

    def get(self):
        logger.info(f"work-all endpoint called")
        res = self.data_provider.get_all_works()
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
                (r"/pid", WorkHandler, {'data_provider': data_provider, 'stat_collector': STAT}),
                (r"/universe-all", UniversesAllHandler, {'data_provider': data_provider, 'stat_collector': STAT}),
                (r"/series-all", SeriesAllHandler, {'data_provider': data_provider, 'stat_collector': STAT}),
                (r"/pid-all", WorkAllHandler, {'data_provider': data_provider, 'stat_collector': STAT})
            ]
    return tw.Application(handlers)

def main(args):
    port = args.port
    ab_id = args.ab_id
    data_dir = args.data_dir
    works_dict: dict = {}
    series_dict: dict = {}
    universe_dict: dict = {}
    if not 'LOWELL_URL' in os.environ:
        logger.error("LOWELL_URL not set")
        import sys
        sys.exit(-1)
    if data_dir:
        logger.info(f"Reading data files from {data_dir}")
        json_files = [json_file for json_file in os.listdir(data_dir) if json_file.endswith('.json')]
        for jf in json_files:
            logger.info(f"reading json file {jf}")
            works_dict, series_dict, universe_dict = read_json_file(data_dir, jf, works_dict, series_dict, universe_dict)
    works_list = works_dict.keys()
    logger.info(f"Reading works metadata for {len(works_list)} keys...")
    pid2metadata = lmf.pid2metadata(works_list)
    logger.info("done reading metadata")
    data_provider = DataProvider(works_dict, series_dict, universe_dict, pid2metadata)
    app = make_app(ab_id, data_provider)

    logger.info(f"service up at port {port}")
    app.listen(port)
    ti.IOLoop.current().start()

def read_json_file(path, filename, input_works_dict, input_series_dict, input_universe_dict):
    works_dict: dict = input_works_dict
    series_dict: dict = input_series_dict
    universe_dict: dict = input_universe_dict
    with open(os.path.join(path, filename)) as fp:
        obj_list = json5.load(fp)
        for obj in obj_list:
            if "universeTitle" in obj and not obj["universeTitle"] in universe_dict:
                universe_description = obj.get("universeDescription", None)
                universe_alternative_title_str = obj.get("universeAlternativeTitle", None)
                universe_alternative_title = universe_alternative_title_str if universe_alternative_title_str else None
                universe = Universe(obj["universeTitle"], universe_description, universe_alternative_title)
                universe_dict[obj["universeTitle"]] = universe
        for obj in obj_list:
            if "seriesTitle" in obj and not obj["seriesTitle"] in series_dict:
                series_descr = obj.get("seriesDescription", None)
                number_in_universe_str = obj.get("numberInUniverse", None)
                number_in_universe = int(number_in_universe_str) if number_in_universe_str  else None
                alternative_title_str = obj.get("seriesAlternativeTitle", None)
                series_alternative_title = alternative_title_str if alternative_title_str else None
                universe = universe_dict[obj["universeTitle"]] if "universeTitle" in obj else None
                series = Series(series_title=obj["seriesTitle"], series_description=series_descr, number_in_universe=number_in_universe, universe=universe, series_alternative_title=series_alternative_title)
                series_dict[obj["seriesTitle"]] = series
                universe = universe_dict.get(obj['universeTitle'], None) if 'universeTitle' in obj else None
                if universe:
                    universe.included_series.add(series.series_title)
        for obj in obj_list:
            if "workId" in obj:
                series = series_dict.get(obj["seriesTitle"], None) if "seriesTitle" in obj else None
                universe = universe_dict.get(obj['universeTitle'], None) if 'universeTitle' in obj else None
                number_in_series_str = obj.get("numberInSeries", None)
                number_in_series = [float(s) for s in number_in_series_str] if number_in_series_str else None
                if not obj["workId"] in works_dict: # this is a work we have not seen before
                    universe = universe_dict.get(obj["universeTitle"], None) if "universeTitle" in obj else None
                    can_be_read_independently = obj.get("canBeReadIndependently", False)
                    work = Work(workid=obj["workId"], series_memberships={series.series_title: number_in_series} if series else { }, can_be_read_independently=can_be_read_independently, universe=universe)
                    works_dict[obj["workId"]] = work
                else:
                    work = works_dict.get(obj["workId"])
                    if work and series:
                        work.series_memberships[series.series_title] = number_in_series
                if series:
                    series.included_works.add(work.workid)
                if universe:
                    universe.included_works.add(work.workid)
    return works_dict, series_dict, universe_dict

def series_num(workid, works_dict, series_title):
    work = works_dict.get(workid, None)
    if not work:
        return 100000
    sm = work.series_memberships.get(series_title, None)
    if not sm:
        return 100000
    return min(sm, default=100000)

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

