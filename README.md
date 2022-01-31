# RHSSO Auto Deploy
This is a simple Python script which will deploy an exported realm (`realm-export.json`) from Keycloak or RHSSO into a Keycloak or RHSSO instance.
It allows for simple cloning of your existing RHSSO realm and client setup.

This script is also designed to work as a containerised application, so it can be easily be deployed as a Job in OpenShift or Kubernetes.

## Prerequisites
### To build the container image
- `docker` or `podman`
- An exported `realm-export.json` file

### To run the script
- `python` (Minimum of 3.6, tested with 3.9)
- `pip`
  - `requests` library from `pip`
- A Keycloak or RHSSO instance to configure

## Getting Started

### Run locally
This script is also able to run outside of a containerised environment.

First you need to set three environment variables. This can be done by running the following in the terminal:
```bash
export RHSSO_BASE_URL=url_to_your_rhsso_instance
export RHSSO_ADMIN_USER=admin
export RHSSO_ADMIN_PASSWORD=the_admin_password
```

Put your `realm-export.json` file in the root of this directory.

Then simply run the python script as so:
```bash
python main.py
```

### Build as an image
Navigate to the root directory of this project and build the image using `docker` or `podman` and run the following command.
```
docker build -t rhsso-auto-deploy .
```

### Run as a container
When running the application as a container, you need to pass the relevant environment variables to the container. This can be done through the `-e` flag.

```bash
docker run --name bank-rhsso-config \
-e RHSSO_BASE_URL=url_to_your_rhsso_instance \
-e RHSSO_ADMIN_USER=admin \
-e RHSSO_ADMIN_PASSWORD=the_admin_password rhsso-auto-deploy
```

## Environment variables
In order to run the script, some environment variables need to be defined in the environment the script is running in. These are not set at build time.

They are defined as follows:
|Variable name|Description|
|-|-|
|RHSSO_BASE_URL|The base of the URL of your RHSSO or Keycloak instance. URLs for API calls are built on this base.|
|RHSSO_ADMIN_USER|The username of the admin user on RHSSO/Keycloak. This admin needs to be part of the `master` realm.|
|RHSSO_ADMIN_PASSWORD|The password for the admin user explained above.|

## Running in Kubernetes or OpenShift
This script is designed to be ran as a Job in a Kubernetes-like environment. This Job will run a container containing this script once using the environment variables provided to it. 

You will likely need to push an image of this script with your realm export to a container registry that your cluster can reach.

It is recommended that you get the admin username and password from a Secret or similarly secure resource. 

### Example Job
```yaml
kind: Job
apiVersion: batch/v1
metadata:
  name: app-rhsso-config
  namespace: my-application
  labels:
    app: app-rhsso-config
spec:
  template:
    metadata:
      name: app-rhsso-config
    spec:
      containers:
        - name: app-rhsso-config
          image: quay.io/my-user/my-app-rhsso-config
          envFrom:
            - secretRef:
                name: rhsso-secrets
          imagePullPolicy: Always
      restartPolicy: Never
```