# Python Coreference Resolver Service

Our service based alternative to Coreference Resolution. 

# Notes

Useful hints that can save you some time. 

## Python Interpreter

>=Python 3.5

## Running locally

Install dependencies.

```bash
pip install -r requirements.txt
pip install uwsgi
```

This will start the service locally bound to `0.0.0.0:5128`.

```bash
cd src
uwsgi --ini uwsgi.ini
```

You must have a CoreNLP server running at `http://corenlp:9000`. If not,
change it in `Resolver.py` to your instance.

## Running within a Docker Container

```bash
docker-compose up
```

## Testing


```bash
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
