# Python Coreference Resolver Service

Our service-based alternative to Coreference Resolution. 


## Python Interpreter

**Python 3.5 or 3.6**

The docker container is using 3.6.1.

## Running locally

Install dependencies, best inside a virtual environment.

```bash
pip install -r requirements.txt
pip install uwsgi
```

This will start the service locally bound to `0.0.0.0:5128`.

```bash
cd src
uwsgi --ini uwsgi.ini
```

You must have a CoreNLP server running somewhere. You can configure it with the environmental variable `PYCOBALT_CORENLP=http://localhost:9000`.
If you are not using [our docker image](https://hub.docker.com/r/lambdacube/corenlp) which includes the required models, you must have the following models in the server's classpath:
- stanford-corenlp-models-current.jar
- stanford-english-corenlp-models-current.jar
- stanford-english-kbp-corenlp-models-current.jar

It is using CoreNLP version 3.7.0.

## Running within a Docker Container

The service is wrapped in the `docker-compose.yml` file which also includes an instance of CoreNLP.

```bash
docker-compose up
```

## Testing

```bash
curl -X POST \
 -H "Content-Type: application/json" \
 -H "Accept: application/json" \
 -d '{"text": "Donald Trump is the president of USA. He is a business man."}' \
 "http://localhost:5128/resolve/text"
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
