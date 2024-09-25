# Pollinator
**Pollinator** is a Command Line Interface (CLI) tool designed to streamline deployment of batch jobs on **ColonyOS**. It leverages **ColonyFS** for transferring data to container executors, allowing users to experience a local working environment as much as possible.

Pollinator significantly simplifies interactions with HPC or Kubernetes systems. For instance, it completely eliminates the need to manually log in to HPC nodes to run Slurm jobs. It seamlessly synchronizes and transfers data from the user’s local filesystem to remote executors, offering the convenience of a local development environment while harnessing powerful supercomputers and cloud platforms. With Pollinator, users are no longer required to have in-depth knowledge of Slurm or Kubernetes systems. It can also automatically set up SSH tunnels to processes running on a Slurm cluster, making it very convenient to run Jupyter notebooks on HPC.

## Installation
The Pollinator CLI can be downloaded [here](https://github.com/colonyos/pollinator/releases). Linux, Window, and Apple is supported.

Copy the binary to directory availble in the *PATH* e.g. **/usr/local/bin**.  

```bash
sudo cp pollinator /use/local/bin
```

```bash
pollinator --help
```

On MacOS there is an error first time you run it. You need to grant Pollinator permission to execute. Open System Settings, go to Privacy & Security, and click on the *Allow* button next to *pollinator* to enable it to execute.

## Creating a new project
Make sure the dev environment is running. See [Tutorial 1](../1-getting-started/tutorial.md).

```bash
source docker-compose.env
mkdir testproj;cd testproj
pollinator new -n dev-docker
```

```console
INFO[0000] Creating directory                            Dir=./cfs/src
INFO[0000] Creating directory                            Dir=./cfs/data
INFO[0000] Creating directory                            Dir=./cfs/result
INFO[0000] Generating                                    Filename=./project.yaml
INFO[0000] Generating                                    Filename=./cfs/data/hello.txt
INFO[0000] Generating                                    Filename=./cfs/src/main.py
```

As you can see, several files and directories were generated. The directories under *./cfs* are automatically synchronized to ColonyFS. The table below explains how they are synchronized:

| Directory   | Sync Strategies                                                                              |
|-------------|----------------------------------------------------------------------------------------------|
| `cfs/src`   | Synchronized to the container before the process starts. Removed after the process completes. |
| `cfs/data`  | Synchronized to the container before the process starts. Retained on the executor's file system after the process completes. |
| `cfs/result`| Synchronized after the process completes, and then synchronized back to the client.          |

The *project.yml* contains project settings and will be used to generate a function spec. It is assumed that *source* is located in *./cfs/src*.

```yaml
projectname: 7a0289837f0f0f93ce6f0c219968b806a453ff275b750bf055f2a2116ea4a121
conditions:
  executorNames:
  - dev-docker
  nodes: 1
  processesPerNode: 1
  cpu: 1000m
  mem: 1000Mi
  walltime: 600
  gpu:
    count: 0
    name: ""
environment:
  docker: python:3.12-rc-bookworm
  rebuildImage: false
  init-cmd: pip3 install numpy
  cmd: python3
  source: main.py
tunnel: null
```

This is the content of *main.py*:

```python
import os
import socket

# Print the hostname
hostname = socket.gethostname()
print("hostname:", hostname)

# The projdir is the location on the executor where project dirs have been synced
projdir = str(os.environ.get("PROJECT_DIR"))

# The processid is the unique id of the process where this code will execute at a remove executor
processid = os.environ.get("COLONIES_PROCESS_ID")

print("projdir:", projdir)
print("processid:", processid)

# Open the hello.txt file and print the content
file = open(projdir + "/data/hello.txt", 'r')
contents = file.read()
print(contents)

# Write the result to the a file in the result dir
result_dir = projdir + "/result/"
os.makedirs(result_dir, exist_ok=True)

file = open(result_dir + "/result.txt", "w")
file.write("Hello, World!")
file.close()⏎
```

## Run the project
To run the project and execute *./cfs/src/main.py*:

```bash
pollinator run --follow
```

```console
Analyzing /home/johan/dev/github/colony~ ... done!

Uploading /pollinator/7a0289837f0f0f93c~ ... done! [788B]

Analyzing /home/johan/dev/github/colony~ ... done!

Uploading /pollinator/7a0289837f0f0f93c~ ... done! [12B]

INFO[0000] Process submitted                             ProcessID=97afce6f4c2392554045350432002b205c6a880a7da68a76ea5528d022806923
INFO[0000] Follow process at https://dashboard.colonyos.io/process?processid=97afce6f4c2392554045350432002b205c6a880a7da68a76ea5528d022806923
INFO[0000] Process started                               ProcessID=97afce6f4c2392554045350432002b205c6a880a7da68a76ea5528d022806923
Pulling from library/python
Digest: sha256:1c46d992e89efe3179bf5450efdff3c28ad3c56b44a9d7b24202943450d146b6
Status: Image is up to date for python:3.12-rc-bookworm
Collecting numpy
  Obtaining dependency information for numpy from https://files.pythonhosted.org/packages/28/95/b56fc6b2abe37c03923b50415df483cf93e09e7438872280a5486131d804/numpy-2.0.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata
  Downloading numpy-2.0.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (60 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 60.9/60.9 kB 3.0 MB/s eta 0:00:00
Downloading numpy-2.0.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (19.0 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 19.0/19.0 MB 50.9 MB/s eta 0:00:00
Installing collected packages: numpy
Successfully installed numpy-2.0.0
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv

[notice] A new release of pip is available: 23.2.1 -> 24.1.1
[notice] To update, run: pip install --upgrade pip
hostname: 8d3290a9db34
projdir: /cfs/pollinator/7a0289837f0f0f93ce6f0c219968b806a453ff275b750bf055f2a2116ea4a121
processid: 97afce6f4c2392554045350432002b205c6a880a7da68a76ea5528d022806923
Hello world!
INFO[0006] Process finished successfully                 ProcessID=97afce6f4c2392554045350432002b205c6a880a7da68a76ea5528d022806923
Downloading /home/johan/dev/github/colo~ ... done! [13B]
```

If we look in ColonyFS we can see that several new labels have been created:

```bash
colonies fs label ls
```

```console
╭─────────────────────────────────────────────────────────────────────────────────────┬───────╮
│ LABEL                                                                               │ FILES │
├─────────────────────────────────────────────────────────────────────────────────────┼───────┤
│ /pollinator/7a0289837f0f0f93ce6f0c219968b806a453ff275b750bf055f2a2116ea4a121/src    │ 1     │
│ /pollinator/7a0289837f0f0f93ce6f0c219968b806a453ff275b750bf055f2a2116ea4a121/result │ 1     │
│ /pollinator/7a0289837f0f0f93ce6f0c219968b806a453ff275b750bf055f2a2116ea4a121/data   │ 1     │
╰─────────────────────────────────────────────────────────────────────────────────────┴───────╯
```

We can also search for logs:

```bash
colonies log search --text "hello" -d 30
```

```console
INFO[0000] Searching for logs                            Count=20 Days=30 Text=hello
╭──────────────┬──────────────────────────────────────────────────────────────────╮
│ Timestamp    │ 2024-07-03 09:20:52                                              │
│ ExecutorName │ dev-docker                                                       │
│ ProcessID    │ 97afce6f4c2392554045350432002b205c6a880a7da68a76ea5528d022806923 │
│ Text         │ Hello world!                                                     │
╰──────────────┴──────────────────────────────────────────────────────────────────╯
```
