# Deployment with docker

## Build base container:

First you need to create the base container that will be used for the wsgi app and celery

```
docker build -t lwosf -f Dockerfile.lwosf .
```

## Build compose containers:

```
docker-compose build
```

## Extra configuration:

Containers are ready to run the Open Science Framework, although some features require exta configuration 


