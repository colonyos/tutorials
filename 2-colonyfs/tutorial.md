# ColonyFS
To efficiently manage data, ColonyOS provides a meta-filesystem called the Colony Filesystem (ColonyFS). Unlike a traditional filesystem, ColonyFS doesn't store the actual files but rather stores metadata about the files. This metadata includes information such as file names, checksums, Internet addresses of servers from which to fetch data, details about the protocols used, and optionally, credentials for accessing the files. 

ColonyFS currently supports S3, but it is architecturally designed to support any type of protocol and storage technology, for example the [InterPlanetary File System (IPFS)](https://ipfs.tech).

## Immutability
ColonyFS was primarily designed to manage machine learning tasks. Given that machine learning datasets sometimes can be quite large, efficient caching of data is crucial. In ColonyFS, all files are immutable, meaning they cannot be altered but only completely replaced. This approach simplifies caching of files that are part of labels and snapshots, as the immutability guarantees the consistency and reliability of the data being cached.

Since files cannot be altered once created, this also reduces the risk of data tampering and unauthorized modifications. Immutability ensures that data remains in its original, unaltered state, and thus provide a more secure environment where data integrity can be maintained over time.

Another reason of immutability is prevention of race conditions. In computing, a race condition occurs when multiple processes access and manipulate the same data concurrently, leading to inconsistent or unexpected results. Since immutable files cannot be modified once they are created, this effectively eliminates the possibility of race conditions related to file modifications. This ensures that when a file is read, it cannot be changed by another process at the same time, leading to more predictable and reliable system behavior. By using immutable files, ColonyFS enables stable and consistent data handling across various executors.

## Snapshots
Additionally, ColonyFS offers functionality to create *snapshots*. This feature is essential for generating immutable copies of whole directory trees, which can include source code or data intended for execution or processing. Since processes can be queued and may have to wait before execution, snapshots ensure that the referenced data remains unaltered or that files cannot be added or removed to certain label while the process is in the queue, awaiting execution.

This tutorial will explain how to use ColonyFS.

## Setting up a development environment
The following commands will use Docker Compose to set up and configure a Colonies server, a TimescaleDB, a Minio serve  r, and a Docker Executor. To set up a production environment, it is recommended to use Kubernetes.

*Note!* The *docker-compose.env* file contains credentials and configuration and must be sourced before using the Colo  nies CLI command.

```bash
wget https://raw.githubusercontent.com/colonyos/colonies/main/docker-compose.env;                    source docker-compose.env;
wget https://raw.githubusercontent.com/colonyos/colonies/main/docker-compose.yml;
docker-compose up
```

## Installing the Colonies CLI
The Colonies CLI can be downloaded [here](https://github.com/colonyos/colonies/releases). Linux, Window, and Apple is supported.

  Start another terminal and run the command below to load the credentials and settings, allowing the Colonies CLI to co  nnect to the Colonies server started with Docker compose.
  ```bash
  source docker-compose.env
  ```

## Uploading and synching files
Let's upload some files to ColonyFS. 

```bash
mkdir myfiles; echo 'This is my file!' >> myfiles/myfile.txt
```

Now upload the myfiles directory to ColonyFS under the label myfiles.

```bash
colonies fs sync -l myfiles -d ./myfiles --yes
```

```console
INFO[0000] Calculating sync plans
Analyzing /home/johan/test/myfiles       ... done!

INFO[0000] Sync plans completed                          Conflict resolution=replace-remote Conflicts=0 Download=0 Upload=1
INFO[0000] Add --syncplans flag to view the sync plan in more detail

Uploading /myfiles                       ... done! [17B]
```

## Listing labels and files
Let's list all labels.

```bash
colonies fs label ls
```

```console
╭──────────┬───────╮
│ LABEL    │ FILES │
├──────────┼───────┤
│ /myfiles │ 1     │
╰──────────┴───────╯
```

List all files in the */myfiles* label.
```bash
colonies fs ls -l /myfiles
```

```console
╭────────────┬───────┬──────────────────────────────────────────────────────────────────┬─────────────────────┬───────────╮
│ FILENAME   │ SIZE  │ LATEST ID                                                        │ ADDED               │ REVISIONS │
├────────────┼───────┼──────────────────────────────────────────────────────────────────┼─────────────────────┼───────────┤
│ myfile.txt │ 0 KiB │ da191d7bca0e02d41ac77569de0c57c9f1970f1466f835424076d65c0e967e53 │ 2024-06-30 12:37:14 │ 1         │
╰────────────┴───────┴──────────────────────────────────────────────────────────────────┴─────────────────────┴───────────╯
```

The command below shows information about the myfile.txt file. Note that ColonyFS only contains metadata about files, and not the actual data. The information below can be used by the Docker Executor to fetch the data.

```bash
colonies fs info -n myfile.txt -l /myfiles
```

```console
╭─────────────────┬──────────────────────────────────────────────────────────────────╮
│ Filename        │ myfile.txt                                                       │
│ FileId          │ da191d7bca0e02d41ac77569de0c57c9f1970f1466f835424076d65c0e967e53 │
│ Added           │ 2024-06-30 12:37:14                                              │
│ Sequence Number │ 1                                                                │
│ Label           │ /myfiles                                                         │
│ Colony          │ dev                                                              │
│ Size            │ 0 KiB                                                            │
│ Checksum        │ 9ba8a876f448a526f12482b2dc18a617a9c7b5e20e86966d4a588faa24a3c598 │
│ Checksum Alg    │ SHA256                                                           │
│ Protocol        │ s3                                                               │
│ S3 Endpoint     │ localhost:9000                                                   │
│ S3 TLS          │ false                                                            │
│ S3 Region       │                                                                  │
│ S3 Bucket       │ colonies-prod                                                    │
│ S3 Object       │ 469b3dc71909aaa9f78099254ae40bef0fd0b2a5e00bda8989281a09b4ae71d7 │
│ S3 Accesskey    │ ******************************                                   │
│ S3 Secretkey    │ ******************************                                   │
│ Encryption Key  │ ******************************                                   │
│ Encryption Alg  │                                                                  │
╰─────────────────┴──────────────────────────────────────────────────────────────────╯
```

## Using ColonyFS in jobs
Let's submit a job that process the *myfile.txt* file. The *fs* block in the JSON below contains instructions how to synchronize the */myfiles* label with the directory */cfs/myfiles* accessible by the container launched by the Docker Executor.

```json
{
    "conditions": {
        "executortype": "container-executor",
        "executornames": [
            "dev-docker"
        ],
        "nodes": 1,
        "processespernode": 1,
        "mem": "10Gi",
        "cpu": "1000m",
        "gpu": {
            "count": 0
        },
        "walltime": 60
    },
    "funcname": "execute",
    "kwargs": {
        "cmd": "cat /cfs/myfiles/myfile.txt",
        "docker-image": "ubuntu:20.04"
    },
    "maxexectime": 55,
    "maxretries": 3,
    "fs": {
        "mount": "/cfs",
        "dirs": [
            {
                "label": "/myfiles",
                "dir": "/myfiles",
                "keepfiles": false,
                "onconflicts": {
                    "onstart": {
                        "keeplocal": false
                    },
                    "onclose": {
                        "keeplocal": false
                    }
                }
            }
        ]
    }
}
```

The following command will launch a process that prints the content of the *myfile.txt*.

```bash
colonies function submit --spec cat.json --follow
```

```console
INFO[0000] Process submitted                             ProcessId=501e1a9f893b881ee22b589cd2c2fc41da8a6d108d5864610ccca0e9e4046295
INFO[0000] Printing logs from process                    ProcessId=501e1a9f893b881ee22b589cd2c2fc41da8a6d108d5864610ccca0e9e4046295
Pulling from library/ubuntu
Digest: sha256:0b897358ff6624825fb50d20ffb605ab0eaea77ced0adb8c6a4b756513dec6fc
Status: Image is up to date for ubuntu:20.04
This is my file!
INFO[0002] Process finished successfully                 ProcessId=501e1a9f893b881ee22b589cd2c2fc41da8a6d108d5864610ccca0e9e4046295
```

It is also possible for a process to generate data. Note that *keeplocal* on *onclose* is set to *true*. This is make sure that the *result.txt* is overwritten after the process terminates. 

```json
{
    "conditions": {
        "executortype": "container-executor",
        "executornames": [
            "dev-docker"
        ],
        "nodes": 1,
        "processespernode": 1,
        "mem": "10Gi",
        "cpu": "1000m",
        "gpu": {
            "count": 0
        },
        "walltime": 60
    },
    "funcname": "execute",
    "kwargs": {
        "cmd": "echo 'process says hi!' >> /cfs/output/result.txt",
        "docker-image": "ubuntu:20.04"
    },
    "maxexectime": 55,
    "maxretries": 3,
    "fs": {
        "mount": "/cfs",
        "dirs": [
            {
                "label": "/output",
                "dir": "/output",
                "keepfiles": false,
                "onconflicts": {
                    "onstart": {
                        "keeplocal": false
                    },
                    "onclose": {
                        "keeplocal": true 
                    }
                }
            }
        ]
    }
}
```

```bash
colonies function submit --spec gen_file.json --follow
```

```console
INFO[0000] Process submitted                             ProcessId=b09482e4256fc02d0db3279a1dea62a606b2cd1eb1418c415c24bf06300ea34c
INFO[0000] Printing logs from process                    ProcessId=b09482e4256fc02d0db3279a1dea62a606b2cd1eb1418c415c24bf06300ea34c
Pulling from library/ubuntu
Digest: sha256:0b897358ff6624825fb50d20ffb605ab0eaea77ced0adb8c6a4b756513dec6fc
Status: Image is up to date for ubuntu:20.04
INFO[0002] Process finished successfully                 ProcessId=b09482e4256fc02d0db3279a1dea62a606b2cd1eb1418c415c24bf06300ea34c
rocinante (test) >>> colonies fs label ls
```

Now there should be new label called */output* created.

```bash
colonies fs label ls
```

```console
╭──────────┬───────╮
│ LABEL    │ FILES │
├──────────┼───────┤
│ /output  │ 1     │
│ /myfiles │ 1     │
╰──────────┴───────╯
```

Finally, let's synchronize */output* to our local computer.

```bash
colonies fs sync -l /output -d ./output --yes
```

```console
INFO[0000] Calculating sync plans
Downloading /home/johan/test/output      ... done! [17B]
```

```bash
cat ./output/result.txt
```

```console
process says hi!
```

## Snapshots
Is is also possible to store source code in ColonyFS and launch processes that use the source code.

Let's create a file called *src/helloworld.py* with the content below, and then upload it to ColonyFS.
```python
print("Hello, World!")
```

```bash
mkdir -p src && echo 'print("Hello, World!")' > src/helloworld.py; colonies fs sync -l src -d ./src --yes 
```

```bash
colonies fs label ls                                             13:52:33
```

```console
╭──────────┬───────╮
│ LABEL    │ FILES │
├──────────┼───────┤
│ /src     │ 1     │
│ /output  │ 1     │
│ /myfiles │ 1     │
╰──────────┴───────╯
```

```json
{
    "conditions": {
        "executortype": "container-executor",
        "executornames": [
            "dev-docker"
        ],
        "nodes": 1,
        "processespernode": 1,
        "mem": "10Gi",
        "cpu": "1000m",
        "gpu": {
            "count": 0
        },
        "walltime": 60
    },
    "funcname": "execute",
    "kwargs": {
        "cmd": "python3",
        "docker-image": "python",
         "args": [
            "/cfs/src/helloworld.py"
        ]
    },
    "maxexectime": 55,
    "maxretries": 3,
    "fs": {
        "mount": "/cfs",
        "dirs": [
            {
                "label": "/src",
                "dir": "/src",
                "keepfiles": false,
                "onconflicts": {
                    "onstart": {
                        "keeplocal": false
                    },
                    "onclose": {
                        "keeplocal": false 
                    }
                }
            }
        ]
    }
}
```

```bash
colonies function submit --spec python.json --follow
```

```console
INFO[0000] Process submitted                             ProcessId=9db7a2d0bed6ab59ebe9539db2e180c66f352adb1679caf79ebd3a70da60a82e
INFO[0000] Printing logs from process                    ProcessId=9db7a2d0bed6ab59ebe9539db2e180c66f352adb1679caf79ebd3a70da60a82e
Pulling from library/python
Digest: sha256:fce9bc7648ef917a5ab67176cf1c7eb41b110452e259736144bc22f32f3aa622
Status: Image is up to date for python:latest
Hello, World!
INFO[0005] Process finished successfully                 ProcessId=9db7a2d0bed6ab59ebe9539db2e180c66f352adb1679caf79ebd3a70da60a82e
```

That worked fine! We successfully called the Python source code uploaded to ColonyFS. However, there is a potential problem. What happens if the process is queued for a long time and the source code is modified? This means that the execution might not reflect the original code, leading to inconsistencies or unexpected behavior.

A solution to this problem is to use snapshots. A snapshot is an immutable copy of a label. 

```bash
colonies fs snapshot create -l /src -n mysnapshot
```

```console
INFO[0000] Snapshot created                              Label=/src/ SnapshotName=mysnapshot
╭────────────┬──────────────────────────────────────────────────────────────────╮
│ SnapshotId │ 6fbc7fffa54c53620427792c57ac3324b508a4405a9173e70f2e6da4bc2393a6 │
│ Name       │ mysnapshot                                                       │
│ Label      │ /src                                                             │
│ Colony     │ dev                                                              │
│ Added      │ 2024-06-30 12:09:10                                              │
╰────────────┴──────────────────────────────────────────────────────────────────╯
╭───────────────┬──────────────────────────────────────────────────────────────────┬─────────────────────╮
│ FILENAME      │ FILEID                                                           │ ADDED               │
├───────────────┼──────────────────────────────────────────────────────────────────┼─────────────────────┤
│ helloworld.py │ d9c7e36ac420bb536a7aaa9c01dd4c2aae99d7bb9c870724db743d8ad230bcfb │ 2024-06-30 14:07:14 │
╰───────────────┴──────────────────────────────────────────────────────────────────┴─────────────────────╯
```

Let's modify the JSON to use snapshots instead of syncing directories.
```json
{
    "conditions": {
        "executortype": "container-executor",
        "executornames": [
            "dev-docker"
        ],
        "nodes": 1,
        "processespernode": 1,
        "mem": "10Gi",
        "cpu": "1000m",
        "gpu": {
            "count": 0
        },
        "walltime": 60
    },
    "funcname": "execute",
    "kwargs": {
        "cmd": "python3",
        "docker-image": "python",
         "args": [
            "/cfs/src/helloworld.py"
        ]
    },
    "maxexectime": 55,
    "maxretries": 3,
    "fs": {
        "mount": "/cfs",
        "snapshots": [
            {
                "snapshotid": "6fbc7fffa54c53620427792c57ac3324b508a4405a9173e70f2e6da4bc2393a6",
                "dir": "/src",
                "keepfiles": false,
                "keepsnapshot": true 
            }
        ]
    }
}
```

```bash
colonies function submit --spec python_snapshot.json --follow
```

```console
INFO[0000] Process submitted                             ProcessId=9725d7176990951a233c0ddddcda86032a2f3e25d7a366e7284d754055d3b529
INFO[0000] Printing logs from process                    ProcessId=9725d7176990951a233c0ddddcda86032a2f3e25d7a366e7284d754055d3b529
Pulling from library/python
Digest: sha256:fce9bc7648ef917a5ab67176cf1c7eb41b110452e259736144bc22f32f3aa622
Status: Image is up to date for python:latest
Hello, World!
INFO[0002] Process finished successfully                 ProcessId=9725d7176990951a233c0ddddcda86032a2f3e25d7a366e7284d754055d3b529
```

### Using the Colones CLI to automatically generate snapshots
Instead of manually creating snapshots, the Colonies CLI can automatically create a snaphots and fill in the *snapshotid*. Instead of *snapshotid* we must specify a *label* in the *snapshots* field. We must also **--snapshot** flag to the Colonies CLI when submitting the function spec. 

```json
{
    "conditions": {
        "executortype": "container-executor",
        "executornames": [
            "dev-docker"
        ],
        "nodes": 1,
        "processespernode": 1,
        "mem": "10Gi",
        "cpu": "1000m",
        "gpu": {
            "count": 0
        },
        "walltime": 60
    },
    "funcname": "execute",
    "kwargs": {
        "cmd": "python3",
        "docker-image": "python",
         "args": [
            "/cfs/src/helloworld.py"
        ]
    },
    "maxexectime": 55,
    "maxretries": 3,
    "fs": {
        "mount": "/cfs",
        "snapshots": [
            {
                "label": "/src",
                "dir": "/src",
                "keepfiles": false,
                "keepsnapshot": false
            }
        ]
    }
}
```

```bash
colonies function submit --spec python_snapshot.json --snapshot --follow
```

Since we automatically create a snapshot for every submit call and never reuse a snapshot, it is best practice to set *keepsnapshot* to *false* to automatically removed used snapshots.
