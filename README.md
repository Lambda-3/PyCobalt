# Python Coreference Resolver Service

Our service based alternative to Coreference Resolution. 

# Notes

Useful hints that can save you some time. 

## Python Interpreter

__Python 3.5.x__

Python 3.6 should also work but is not tested.

## Running locally

Install dependencies.

```
$ pip install -r requirements.txt
$ pip install uwsgi
```

This will start the service locally bound to `0.0.0.0:5128`.

```
$ cd src
$ uwsgi --ini uwsgi.ini
```

You must have a CoreNLP server running at `http://corenlp:9000`. If not,
change it in `Resolver.py` to your instance.

## Running within a Docker Container

Build the image.

```
$ docker build -t coreferenece:v1.1.0-beta.2 .
```

Run in background.

```
$ docker run -d --name coreference -p 5128:5128 coreference:v1.1.0-beta.2
```

Look at the container stdout.

```
$ docker logs -f coreference
```


## Testing


```
curl -X POST \
 -H "Content-Type: application/json" \
 -H "Accept: application/json" \
 -d '{"text": "Donald Trump is the president of USA. He is a business man."}' "http://localhost:5128/resolve/text"
```

Expected output:

```json
{
  "text": "Donald Trump is the president of USA. Donal Trump is a business man.",
}
```

# Contributors (alphabetical order)

- Andre Freitas
- Bernhard Bermeitinger
- Siegfried Handschuh
