"""Provide a CLI interface to search for cities."""

from argparse import ArgumentParser
from elasticsearch import Elasticsearch

import sys
import json
import logging

ES_HOSTS = ['localhost:9200']  # This port is exported by docker-compose
LOG_FMT = '[%(name)+16.16s] %(levelname)-7s %(filename)+20.20s:%(lineno)-5d %(asctime)s %(message)s'
logging.basicConfig(
    datefmt='%Y-%m-%d %H:%M:%S',
    format=LOG_FMT,
    level=logging.DEBUG
)
logging.getLogger('elasticsearch').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)


def search(es, query, start, size):
    """Perform the actual search."""
    if not start:
        start = 0

    query['from'] = start

    if not size:
        size = 20

    query['size'] = size

    results = es.search(
        index='places',
        doc_type='place',
        body=query,
        ignore=[404]
    )
    hits = results.get('hits')
    if not hits:
        return -1

    if hits['total'] == 0:
        logging.info('No results for the specified query')
        return 0

    logging.info(json.dumps(
        [r['_source'] for r in results['hits']['hits']],
        indent=2
    ))
    logging.info(
        'Starting at %s, displaying %s of %s',
        start,
        len(results['hits']['hits']),
        hits['total']
    )
    return 1


def search_name(es, name, start, size):
    """Perform the full text name search."""
    query = {
        'query': {
            'constant_score': {
                'filter': {
                    'bool': {
                        'must': [{
                            'match': {
                                'name': {
                                    'query': name,
                                    'fuzziness': 'AUTO',
                                    'operator': 'and',
                                }
                            }
                        }]
                    }
                }
            }
        }
    }

    return search(es, query, start, size)


def search_location(es, lat, lon, radius, start, size):
    """Perform the location search."""
    query = {
        'query': {
            'constant_score': {
                'filter': {
                    'bool': {
                        'must': [
                            {
                                'geo_distance': {
                                    'distance': radius + 'mi',
                                    'search_location': {
                                        'lat': lat,
                                        'lon': lon,
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }
    }

    return search(es, query, start, size)


def main():
    """Perform the search."""
    parser = ArgumentParser()
    parser.add_argument('--name', dest='name', default=None)

    parser.add_argument('--lat', dest='lat', default=None)
    parser.add_argument('--lon', dest='lon', default=None)
    parser.add_argument('--radius', dest='radius', default=None)
    parser.add_argument('--start', dest='start', default=None)
    parser.add_argument('--size', dest='size', default=None)

    args = parser.parse_args()

    if not args.name and not all((args.lat, args.lon, args.radius)):
        print('Invalid opts provided, name or all of lat/lon/radius required')
        return -1

    es = Elasticsearch(
        hosts=ES_HOSTS,
        timeout=120
    )

    if args.name:
        logging.info('Name Search:')
        res = search_name(es, args.name, args.start, args.size)
        if res < 0:
            return res

    if all((args.lat, args.lon, args.radius)):
        logging.info('Location Search:')
        res = search_location(
            es, args.lat, args.lon, args.radius, args.start, args.size
        )
        if res < 0:
            return res


if __name__ == '__main__':
    sys.exit(main())
