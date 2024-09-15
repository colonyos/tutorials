# K8s Executor

## Helm chart
```bash
git clone https://github.com/colonyos/helm
cd helm/colonyos/colonies
```

## Deployment and configuration

```bash
cd helm/colonyos/kubeexecutor
```

Update **values.yaml**, e.g. change:

```console
StorageClass: "TODO"
ColoniesPrvKey: "TODO"
AWSS3Endpoint: "TODO, e.g. s3.colonyos.io:443"
AWSS3AccessKey: "TODO"
AWSS3SecretKey: "TODO"
```

Replicas defines how many executors to deploy.
```console
Replicas: 1
```

It is also necessary to specify the available resources within the namespace/cluster. The K8s Executor will not initiate new processes that exceed these specified resource limits. This prevents overloading the Kubernetes cluster.

```console
ExecutorHWCPU: "250000m"
ExecutorHWModel: "ICE Connect EKS"
ExecutorHWNodes: "29"
ExecutorHWMem: "4360000Mi"
ExecutorHWStorage: "10Gi"
ExecutorHWGPUCount: "4"
ExecutorHWGPUMem: "12GiB"
ExecutorHWGPUNodesCount: "4"
ExecutorHWGPUName: "nvidia_2080ti"
```

```bash
kubectl create namespace k8sexecutor
helm install kubeexecutor -f values.yaml -n k8sexecutor .
```
