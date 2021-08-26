# Task A1
This folder contains a reverse proxy using ngnix, fowarding requests to 2 different webservers (also on nginx). This was chosen to demonstrate better the one of the typical use cases of a reverse proxy, to forward requests to 2 different servers.

## Running the Docker containers
To build the containers:

```docker-compose build```

To run the entire service:

```docker-compose up -d```

Then go to [http://localhost:8080](http://localhost:8080) to view the default page served on the reverse proxy. It contains links to access the different servers hidden behind it, which are networked to the proxy via docker.

This can be verified by looking at the server ip and source url that nginx will replace in the response on each server.

Useful reference for docker-compose: https://docs.microsoft.com/en-us/dotnet/architecture/microservices/multi-container-microservice-net-applications/multi-container-applications-docker-compose