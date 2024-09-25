# Production deployment
This tutorial will guide you through setting up a production environment.

## Installing Kubernetes
First, install [K3s](https://k3s.io) (or some other Kubernetes distribution).

### Let's encrypt
Please note that you need a **valid domain name** to set up TLS and use Let's Encrypt.

If you are using Nginx:
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.10.0/cert-manager.yaml
kubectl create -f letsencrypt_nginx.yaml
```

If you are using Traefik:
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.10.0/cert-manager.yaml
kubectl create -f letsencrypt_traefik.yaml
```

Verify the installation:
```bash
kubectl get pods --namespace cert-manager
```

```console
NAME                                     READY   STATUS    RESTARTS   AGE
cert-manager-646dddd544-rrmx4            1/1     Running   0          19h
cert-manager-cainjector-8676c4b7-dxsjw   1/1     Running   0          19h
```

### Longhorn
You may also want to install Longhorn.

```bash
kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.5.1/deploy/longhorn.yaml
```

## Deploying a Colonies server
First, clone the ColonyOS Helm chart Git repo.

```bash
git clone https://github.com/colonyos/helm
cd helm/colonyos/colonies
```

Update the **values.yaml** file. See [Tutorial-7](../7-security/tutorial.md) how to create a server private key.  
```console
ColoniesServerHostname: "TODO, e.g server.colonyos.io"
ColoniesServerID: "TODO"
ColoniesServerPrvKey: "TODO"
DBPassword: "TODO"
```

Create a namespace:
```bash
kubectl create namespace colonyos
```

Deploy Helm chart:
```bash
helm install colonies -f values.yaml -n colonyos .
```

## Deploying a Minio server

```bash
cd minio
```

Update **values.yaml** file (e.g. credentials) and type:

```bash
helm install ${namespace} -f values.yaml -n ${namespace} .
```

## Post installation
### Env file
Create a **prod.env** file like **docker-compose.env**. Be sure to replace all server addresses, private keys, and IDs with the appropriate production values.

```bash
source prod.env
```

### Setup Minio/S3
First install the Minio client. Instructions can be found [here](https://min.io/docs/minio/linux/reference/minio-mc.html).

Create a Minio account:
```bash
mc alias set myminio http://localhost:9000 $MINIO_USER $MINIO_PASSWORD;
mc admin user add myminio $AWS_S3_ACCESSKEY $AWS_S3_SECRETKEY;
mc admin policy attach myminio readwrite --user=$AWS_S3_ACCESSKEY;
mc mb myminio/$AWS_S3_BUCKET;
```

### Create a Colony
Create a new colony and a new user:

```bash
colonies colony add --name $COLONIES_COLONY_NAME --colonyid $COLONIES_COLONY_ID;
colonies user add --name="myuser" --email="" --phone="" --userid=$COLONIES_ID
```
