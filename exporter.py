import json
import logging
import os
import pathlib
import time

from prometheus_client import start_http_server, Gauge

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
FILE_PATH = os.path.join(APP_PATH, os.path.join('sites.json'))


class GaugeExporterCollector(object):
    def __init__(self):
        self.gauge = Gauge('kafka_consumer_group_offset', 'Help text', ['dataset', 'source', 'zone', 'version'])

    def collect(self):
        exporter_data = {
            'Offset': [],
            'Lag': []
        }

        topics = load_json_file(FILE_PATH)
        for topic in topics:
            exporter_data[topic['data_type']].append({
                'dataset': topic['dataset'],
                'source': topic['source'],
                'zone': topic['zone'],
                'version': topic['version'],
                'value': float(topic['value']),
            })

        for offset in exporter_data['Offset']:
            self.gauge.labels(offset['dataset'], offset['source'], offset['zone'], offset['version']).set(
                offset['value'])


def load_json_file(filename):
    with open(filename, 'r') as json_file:
        return json.load(json_file)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info('starting web server')
    start_http_server(5400)
    logging.info('initializing collector')
    collector = GaugeExporterCollector()
    while True:
        collector.collect()
        time.sleep(5)
