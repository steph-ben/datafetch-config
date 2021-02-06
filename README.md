# datafetch-config

Configuration for fetching weather-related data, mainly using [Prefect](https://prefect.io)


# Getting started

* Setup env

```shell
pip install prefect
```

* Run some flow locally

```shell
$ python laptop/s3_gfs_flow.py run
[2020-12-16 22:04:09+0000] INFO - prefect.FlowRunner | Beginning Flow run for 'aws-gfs-download'
[2020-12-16 22:04:10+0000] INFO - prefect.TaskRunner | Task 'check_run_availability': Starting task run...
[2020-12-16 22:04:10+0000] INFO - prefect.TaskRunner | 20201215 / 0 : Checking run availability ...
[2020-12-16 22:04:26+0000] INFO - prefect.TaskRunner | 20201215 / 0 : Run is available !
...
[2020-12-16 22:05:30+0000] INFO - prefect.TaskRunner | Task 'timestep_9_download': Finished task run for task with final state: 'Success'
[2020-12-16 22:05:30+0000] INFO - prefect.TaskRunner | Task 'timestep_18_download': Finished task run for task with final state: 'Success'
[2020-12-16 22:05:30+0000] INFO - prefect.FlowRunner | Flow run SUCCESS: all reference tasks succeeded
```

Working great ? Now let's run it inside prefect server


* Register and trigger our flow

```shell
# Needed once
$ prefect create project "gfs-fetcher"

# Interacting with Prefect !
$ python laptop/s3_gfs_flow.py register
Result check: OK
Flow URL: http://localhost:8080/default/flow/ec5a906b-6b03-46ce-b7d8-b02e73d30d98
 └── ID: 7f049f56-2c6d-49b4-8515-658b43850764
 └── Project: gfs-fetcher
 └── Labels: ['steph-laptop']
7f049f56-2c6d-49b4-8515-658b43850764

$ python laptop/s3_gfs_flow.py trigger
A new FlowRun has been triggered
Go check it on http://linux:8080/flow-run/1829c2f9-a5f4-43c4-ad3e-bd42a80068ea
```

Enjoy the view !


## Setting-up a full stack with prefect scheduler

### On the server side

* Install prefect lib, cf. https://docs.prefect.io/orchestration/tutorial/overview.html#install-prefect

```shell
# Conda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh ./Miniconda3-latest-Linux-x86_64.sh
conda config --set auto_activate_base false
 
# Create env
conda create -n prefect
conda activate prefect
conda install -c conda-forge prefect
```

* Install Docker, cf. https://docs.docker.com/engine/install/centos/
  
```shell
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io -y
sudo systemctl enable --now docker
sudo docker run hello-world
sudo usermod -Ga docker <<you_user>>
``` 

* Launch prefect server
  
```shell
prefect backend server
prefect server start
```

Now have a look at https://prefect-server:8080


### Launch agent, that will execute flow

On any machine, you can deploy an agent that will actually run the code, cf. https://docs.prefect.io/orchestration/agents/overview.html

* Configure server host https://docs.prefect.io/orchestration/faq/config.html#connecting-to-a-different-api-endpoint

```shell
$ cat ~/.prefect/config.toml
[server]
host = "http://10.0.200.243"
```

* Run either a local agent or a docker agent

```
prefect agent local  start -f --log-level DEBUG
prefect agent docker start -f --log-level DEBUG  -l docker --volume /data:/data
```

### Register your flow

Now that server and agent are ready to use, you can register your flow

```shell
prefect register flow --file ./s3_gfs_flow.py --name fetch-gfs-run12 -p gfs -l docker
prefect run flow --name fetch-gfs-run12 -p gfs --watch
```
