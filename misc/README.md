# Deployment with docker

## Build base container

First you need to create the base container that will be used for the wsgi app and celery

```
docker build -t lwosf-base -f Dockerfile.base .
```

## Build compose containers:

```
docker-compose build
```

## Extra configuration:

The deployment expects the following:

