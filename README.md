# Setup

This system requires Docker compose to start up the infrastructure.

Versions Required:

Docker Engine: 18.02.0+

Docker Compose: 1.21.1

These can be obtained from [Docker](https://www.docker.com/docker-mac)

# Execute

To run the system with full logging
```bash
export DOCKER_KAFKA_HOST=$(ipconfig getifaddr en0)
docker-compose up --scale processor=8
```

To run the system in the background:

```bash
export DOCKER_KAFKA_HOST=$(ipconfig getifaddr en0)
docker-compose up --scale processor=8 -d
```

## Accessing background process logs

You can access logs for the processor using the following:

```bash
docker-compose logs -f processor
```

You can access all logs with the following:

```bash
docker-compose logs -f
```

To submit the files and perform the searches you will need to use the helper files which will require some dependencies to be installed on your submitting machine.

`pip3 install -r processor/requirements.txt`

Now you can submit the file or files using the helper tool.

`python3 process.py /path/to/file/or/directory/or/file/including/paths/to/other/files`

You can query the database using the helper tool.

`python3 search.py -name name`


`python3 search.py --lat 100 --lon 100 --radius 100  # in miles`

Pagination for search can be done using the additional `--start` and `--size` options. Defaults are 0 and 20, respectively.

# Examples

```bash
 $ python3 search.py --name 'san francisco' --start 50 --size 5
[            root] INFO               search.py:135   2018-05-21 12:18:19 Name Search:
[            root] INFO               search.py:49    2018-05-21 12:18:19 [
  {
    "latitude": 19.34564,
    "country": "MX",
    "longitude": -98.86034,
    "shape": "AQAAAH8w8Nx7WDNAM9yAzw+3WMA=",
    "name": "San Francisco Acuautla",
    "admin_2": "039",
    "admin_1": "15",
    "search_location": {
      "lat": 19.34564,
      "lon": -98.86034
    }
  },
  {
    "latitude": 20.55254,
    "country": "MX",
    "longitude": -98.00209,
    "shape": "AQAAAFq77UJzjTRAg2kYPiKAWMA=",
    "name": "San Francisco",
    "admin_2": "083",
    "admin_1": "30",
    "search_location": {
      "lat": 20.55254,
      "lon": -98.00209
    }
  },
  {
    "latitude": 20.65082,
    "country": "MX",
    "longitude": -98.57522,
    "shape": "AQAAAC2VtyOcpjRAVACMZ9CkWMA=",
    "name": "Tlahuelompa (San Francisco Tlahuelompa)",
    "admin_2": "081",
    "admin_1": "13",
    "search_location": {
      "lat": 20.65082,
      "lon": -98.57522
    }
  },
  {
    "latitude": 19.44279,
    "country": "MX",
    "longitude": -99.34398,
    "shape": "AQAAAO/+eK9acTNAmZ6wxAPWWMA=",
    "name": "San Francisco Chimalpa",
    "admin_2": "",
    "admin_1": "17",
    "search_location": {
      "lat": 19.44279,
      "lon": -99.34398
    }
  },
  {
    "latitude": 19.28333,
    "country": "MX",
    "longitude": -99.80917,
    "shape": "AQAAAMb5m1CISDNA4Ln3cMnzWMA=",
    "name": "Loma de San Francisco",
    "admin_2": "118",
    "admin_1": "15",
    "search_location": {
      "lat": 19.28333,
      "lon": -99.80917
    }
  }
]
[            root] INFO               search.py:55    2018-05-21 12:18:19 Starting at 50, displaying 5 of 114

$ python3 search.py --start 0 --size 10 --lon -122.419 --lat 37.7749 --radius 5
[            root] INFO               search.py:141   2018-05-21 12:18:57 Location Search:
[            root] INFO               search.py:49    2018-05-21 12:18:57 [
  {
    "latitude": 37.7966,
    "country": "US",
    "longitude": -122.40858,
    "shape": "AQAAAC7/If325UJALnO6LCaaXsA=",
    "name": "Chinatown",
    "admin_2": "075",
    "admin_1": "CA",
    "search_location": {
      "lat": 37.7966,
      "lon": -122.40858
    }
  },
  {
    "latitude": 37.71715,
    "country": "US",
    "longitude": -122.40433,
    "shape": "AQAAAMcpOpLL20JAq7LviuCZXsA=",
    "name": "Visitacion Valley",
    "admin_2": "075",
    "admin_1": "CA",
    "search_location": {
      "lat": 37.71715,
      "lon": -122.40433
    }
  },
  {
    "latitude": 37.75018,
    "country": "US",
    "longitude": -122.43369,
    "shape": "AQAAAIAO8+UF4EJAi6azk8GbXsA=",
    "name": "Noe Valley",
    "admin_2": "075",
    "admin_1": "CA",
    "search_location": {
      "lat": 37.75018,
      "lon": -122.43369
    }
  },
  {
    "latitude": 37.77493,
    "country": "US",
    "longitude": -122.41942,
    "shape": "AQAAADpY/+cw40JAdNL7xteaXsA=",
    "name": "San Francisco",
    "admin_2": "075",
    "admin_1": "CA",
    "search_location": {
      "lat": 37.77493,
      "lon": -122.41942
    }
  },
  {
    "latitude": 37.75993,
    "country": "US",
    "longitude": -122.41914,
    "shape": "AQAAAOif4GJF4UJAghyUMNOaXsA=",
    "name": "Mission District",
    "admin_2": "075",
    "admin_1": "CA",
    "search_location": {
      "lat": 37.75993,
      "lon": -122.41914
    }
  }
]
[            root] INFO               search.py:55    2018-05-21 12:18:57 Starting at 0, displaying 5 of 5
```



# Troubleshooting

If you have an issue with kafka or elasticsearch when restarting run the following:

```bash
docker-compose rm -fs # to remove and kill all containers
rm -rf volumes  # to remove saved data
```

Then rerun the `docker-compose up` command.

# Discussion

Using the `--scale processor=8` command in docker-compose will spawn 8 processes in a consumer group that will share the load of reading off of Kafka. Obviously the way that the docker-compose is set up right now the bottle neck is in kafka and elasticsearch which are both single node instances.

docker-compose isn't the best platform to scale kafka and elasticsearch, however, so this system still has the same linear "clock" time. A more robust solution would shift to use kubernetes in order to better manage the scaling of kafka and elasticsearch.

docker-compose does give a very clear understanding of how the system might work in production and is a quick tool to set up the environment for devs.

Without having scaling both elasticsearch and kafka we are also susceptible to lost data on outage which isn't ideal.

All of this being said, given a sufficiently well provisioned kafka cluster and elasticsearch cluster I'm pretty confident that this solution would work well.