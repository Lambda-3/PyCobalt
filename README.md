# Python Coreference Resolver Service

Our service based alternative to Coreference Resolution. 

# Notes

Useful hints that can save you some time. 

## Python Interpreter

__Python 3.4.x__. Probably will run on any Python 3x for the development evironment but the deployment will use version __3.4.5__.


## Running locally

Install dependencies.

```
$ pip install -r requirements
```

This will start the service locally bound to `0.0.0.0:5128`.

```
$ python service.py
```

## Running within a Docker Container

Build the image.

```
$ docker build -t coref-resolver:dev .
```

Run in background.

```
$ docker run -d --name coref-resolver -p 5128:5128 coref-resolver:dev
```

Look at the container stdout.

```
$ docker logs -f coref-resolver
```

## Testing


```
curl -X POST \
 -H "Content-Type: application/json" \
 -d '{"text": "Bernhard is working on two projects. He is employed in Mario and PACE."}' "http://localhost:5128/resolve/text"
```

Expected output:

```json
{
  "text": "Donald Trump is the president of USA. He is a business man.",
}

```