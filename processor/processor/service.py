"""
Processor will consume off of the kafka queue and process individual messages.
It will store the transformed messages into elasticsearch cluster for search.
"""
from base64 import b64encode
from elasticsearch import Elasticsearch, ElasticsearchException
from kafka import KafkaConsumer

import logging
import struct

LOG_FMT = '[%(name)+16.16s] %(levelname)-7s %(filename)+20.20s:%(lineno)-5d %(asctime)s %(message)s'
logging.basicConfig(
    datefmt='%Y-%m-%d %H:%M:%S',
    format=LOG_FMT,
    level=logging.DEBUG
)
logging.getLogger('kafka').setLevel(logging.INFO)
logging.getLogger('elasticsearch').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)


# TODO: Load this from a different file
ES_INDEX_DEF = {
    'mappings': {
        'place': {
            'properties': {
                'name': {
                    'type': 'text',
                    'store': True,
                },
                'shape': {
                    'type': 'binary',
                    'store': True,
                },
                'latitude': {
                    'type': 'double',
                    'store': True,
                },
                'longitude': {
                    'type': 'double',
                    'store': True,
                },
                'country': {
                    'type': 'keyword',
                    'store': True,
                },
                'admin_1': {
                    'type': 'keyword',
                    'store': True,
                },
                'admin_2': {
                    'type': 'keyword',
                    'store': True,
                },
                # Used to leverage ES search for nearest locations
                'search_location': {
                    'type': 'geo_point'
                },
            }
        }
    },
    'settings': {
        'index': {
            'number_of_shards': 3,
            'number_of_replicas': 2,
        }
    }
}


def main():
    """Start the consumer and begin processing messages."""
    # TODO: replace the bootstrap server, topic name, and group_id with
    # configuration variables
    consumer = KafkaConsumer(
        'places',
        bootstrap_servers=['kafka:9092'],
        group_id='processor_group_id',
    )

    es = Elasticsearch(
        hosts=['es:9200'],
        timeout=120
    )

    if not es.indices.exists(index='places'):
        # Race condtion on first run with scale > 1
        es.indices.create(
            index='places',
            body=ES_INDEX_DEF,
            update_all_types=True,
            wait_for_active_shards=3,
            ignore=[400]  # hack due to issue with above mentioned race
        )

    ticker = 0

    for msg in consumer:
        # 0. Get the value from the record
        # 1. Split the record
        # 2. verify it's length
        # 3. verify it's content
        # 4. Extract Necessary information
        # 5. Generate shape binary in ESRI format
        #

        split = msg.value.split(b'\t')

        # The record should have 19 fields
        if len(split) != 19:
            err = 'The record provided had an incorrect number of fields: %s'
            logging.error(err, len(split))
            continue

        try:
            geoname_id = int(split[0])
        except ValueError as err:
            logging.error('ID was not integer %s: %s', err, split[0])
            continue

        try:
            lat = float(split[4])
        except ValueError as err:
            logging.error('lat was not a float %s: %s', err, split[5])
            continue

        try:
            lon = float(split[5])
        except ValueError as err:
            logging.error('lat was not a float %s: %s', err, split[6])
            continue

        try:
            name = split[1].decode('utf8')  # this should be UTF8
        except UnicodeDecodeError as err:
            logging.error('Name was supposed to be utf8: %s', err)
            continue

        try:
            country = split[8].decode('ascii')  # should be ascii, 2 chars
            if len(country) != 2:
                logging.error('Invalid length ISO-3166 country: %s', country)
                continue
        except UnicodeDecodeError as err:
            logging.error('Invalid encoding for ISO-3166 country: %s', err)
            continue

        # ADMIN LEVEL 1, this is ISO in US, CH, BE, and ME.
        #   FIPS in all other countries
        try:
            admin_1 = split[10].decode('ascii')  # should still be ascii
        except UnicodeDecodeError as err:
            logging.error('Admin level one encoded incorrectly: %s', err)
            continue

        try:
            admin_2 = split[11].decode('ascii')  # should still be ascii
        except UnicodeDecodeError as err:
            logging.error('Admin level two encoded incorrectly: %s', err)
            continue

        # The geonames data only has enough information to make the
        # point shape, so we will create that and use struct to populate
        # it, format in ESRI is Integer,Double X(lat),Double Y (long),
        # Byte order is little endian, point type is value `1`
        binary_point = struct.pack('<Idd', 1, lat, lon)

        # must be stored as base 64 in ES
        shape = b64encode(binary_point).decode('ascii')

        try:
            es.index(
                index='places',
                doc_type='place',
                id=geoname_id,
                body={
                    'name': name,
                    'shape': shape,
                    'latitude': lat,
                    'longitude': lon,
                    'country': country,
                    'admin_1': admin_1,
                    'admin_2': admin_2,
                    'search_location': {
                        'lat': lat,
                        'lon': lon,
                    }

                }
            )
        except ElasticsearchException as err:
            logging.error('Unable to index the data provided %s', err)

        ticker += 1
        if ticker % 100 == 0:
            logging.info('%s Documents have been indexed', ticker)


if __name__ == '__main__':
    main()
