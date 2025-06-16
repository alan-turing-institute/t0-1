# Reverse proxy

This directory contains the Docker image used to set up the reverse proxy.

The reverse proxy itself is deployed as an Azure Web App:

https://t0-reverse-proxy.azurewebsites.net

This is built from a Docker image in the `t0acr.azurecr.io` container registry.

The web app _should_ be configured to re-deploy whenever a new image is pushed, so updating the web app should be just a matter of pushing a new image to the registry.

## Stopping and starting the proxy

Just stop or start the web app from the Azure Portal.

## Updating the proxy server itself

To do this, you will first need to authenticate.
In the `t0acr` container registry in the Azure Portal, navigate to Settings > Access Keys.
Make sure 'Admin user' is enabled, then copy the given password, and run:


```
docker login t0acr.azurecr.io --username t0acr
```

Enter the password when prompted.

Then, you can build and push the Docker image with the following command (run from this directory).

```
# if you have an Apple Silicon Mac: you need to use this
docker buildx build --platform linux/amd64 --push -t t0acr.azurecr.io/t0-reverse-proxy:latest .

# otherwise
docker build --push -t t0acr.azurecr.io/t0-reverse-proxy:latest .
```

The web app should then update itself.

## Allowing the proxy to access the t0 VM

Inbound traffic to the t0 VM is restricted, so to allow the proxy to function, you will need to add the IP address of the proxy VM to the list of allowed addresses.

To get the IP address of the proxy, run:

```
curl https://t0-reverse-proxy.azurewebsites.net/__ip
```

As of 16 June 2025, the last public IP of the proxy was `20.26.49.55`; this was already added to the allowed addresses for the t0-2 VM.
