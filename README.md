=======
GALAXIA
=======

Infrastructure Monitoring System
--------------------------------

Galaxia is envisioned as a dynamic monitoring system with the following goals

- One single repository for all the monitoring metrics
- On demand dynamic generation of monitoring dashboard
- Capability to export metrics to your favorite systems(orchestrator, analytic engines, alarm systems etc)
- Capability to generate reports
- Capability to generate alerts and notifications
- Capability to bring in intelligence among metrics from various systems
- Complete end to end microservice monitoring from application all the way to infrastructure

### Index

- [Why Galaxia](https://github.com/WiproOpenSourcePractice/galaxia#why-galaxia)
- [Architecture](https://github.com/WiproOpenSourcePractice/galaxia#proposed-architecture)
- [Galaxia Current Capabilities](https://github.com/WiproOpenSourcePractice/galaxia#galaxia-current-capabilities)
- [Future Roadmap](https://github.com/WiproOpenSourcePractice/galaxia#future-roadmap)
- [How Galaxia works?](https://github.com/WiproOpenSourcePractice/galaxia#how-galaxia-works)
- [Set up an ALL-IN-ONE Galaxia]((https://github.com/WiproOpenSourcePractice/galaxia#set

Why Galaxia
-----------
With the advent of cloud & container technologies monitoring needs for
an enterprise has reached multiple folds. Today there is no single open
source solution which provides collecting & co-relating monitoring statistics
from various systems. Some of the pain points today organization face:

-   In a traditional software deployment model an application and most of
    its components will run on a high capacity single server and hence all it
    was required to monitor this single server. Today in a cloud & container
    deployment an application is now broken down into micro services where each
    service may be spread across multiple containers, containers being spread
    across multiple VM’s and VM’s being spread across multiple hosts. In such a
    deployment which is the need of the day it becomes extremely difficult to
    co-relate the metrics from hundreds & thousands of deployment units.

-   Ability to easily visualize real time metrics at different levels and easily narrow down
    to specific resource that you are interested

-   Monitoring needs of an organization often includes
        - Application monitoring which includes monitoring for performance,
          stability, accuracy, log, database & transactions.
        - Infrastructure monitoring which includes monitoring compute
          (RAM, CPU, I/O, Load, Temperature etc), Network (port, switch,
          adapters, interfaces, bridges etc) & Storage.
        - Non-App monitoring which includes monitoring application cluster,
          hardware clusters, software load balancer, hardware load balancer &
          network firewalls
        - Some more may include devops monitoring, code instrumentation, device monitoring
          and many more With so many of above heterogeneous monitoring needs, an enterprise needs
          to maintain multiple metrics repository, multiple end user dashboards & there exists no
          co-relation b/w metrics from so many different sources.


Proposed Architecture
---------------------
< add a diagram here with one line explanation for each component >

** Galaxia Current Capabilities
---------------------------
1) Monitor your docker containers running on bare-metal, virtual machines or your cloud environment
2) Also monitor the underlying infrastructure such as bare-metal, virtual machines or your cloud environment.
3) On demand monitoring dashboard generation either through command line or an intutitive Graphical User Interface
4) On demand monitoring dashboard generation using a regex search
5) Export docker container metrics as a scheduled job to your favorite system for alerts, notifications & alarms,
   currently this functionality is available for OpenStack Ceilometer
6) Ability to list down all the containers, hosts being monitored and their relationship.

Future Roadmap
--------------
- Remove dependency on promdash for dashboard rendering
- Capability to group related dashboards
- Capability to pause, stop and resume outbound exporter jobs
- Capability to generate custom reports
- Capability to subscribe for alerts and notifications
- Capability to bring in intelligence among metrics from various systems and generate an integrated dashboard
- Integrate with another third party metrics renderer like grafana
- Provide capacity planning capabilities via advanced analytics
- Capability to segregate dashboards as per user profile
- Co-relation between metrics and associated drilled down capabilities


How Galaxia works?
------------------
Galaxia works on the concept of exporter, aggregator and renderer. Here exporter is a docker container which exports
metrics to the aggregator. Exporter unit runs on each node from which we wish to capture the metrics. Aggregator
collates metrics from all the exporter in its local database. Renderer connects to aggregator and generates the
monitoring dashboard.


Setup an ALL-IN-ONE Galaxia
----------------------------
Follow the steps below to setup Galaxia, the steps are specific to ubuntu
operating system and hence will have to be modified accordingly for other OS.
We are using vagrant box with ubuntu 14.04 to add up all the components
To successfully operate Galaxia following softwares are required to be installed

- python v2.7
- python pip
- mysql-server
- rabbitmq-server
- Prometheus
- Promdash
- Docker
- cadvisor
- Galaxia

Python v2.7
-----------
Ubuntu comes with Python v2.7 out of the box

Python Pip
----------
Install Python Pip on ubuntu using the following command
sudo apt-get -y install python-pip

mysql-server
------------
Follow the steps below to install mysql-server on ubuntu
```
- sudo apt-get update
- sudo apt-get install -y mysql-server
```

When prompted Set up username as "root" and password as "root".
By default mysql server listens on port 3306.

rabbitmq-server
---------------

```
sudo apt-get install -y rabbitmq-server
```

By default rabbitmq server listens on 5672.

Prometheus
----------
- Download Prometheus version prometheus-0.16.1.linux-amd64.tar.gz from https://github.com/prometheus/prometheus/releases.
  Here is the direct link https://github.com/prometheus/prometheus/releases/download/0.16.1/prometheus-0.16.1.linux-amd64.tar.gz
- Decompress the file prometheus-0.16.1.linux-amd64.tar.gz using the command "tar xzf prometheus-0.16.1.linux-amd64.tar.gz"
- In the root directory create the file prometheus.yml with the following content

```

    # my global config
        global:
            scrape_interval:     15s # By default, scrape targets every 15 seconds.
            evaluation_interval: 15s # By default, scrape targets every 15 seconds.
    # scrape_timeout is set to the global default (10s).

    # Attach these labels to any time series or alerts when communicating with
    # external systems (federation, remote storage, Alertmanager).
    #        external_labels:
    #            monitor: 'codelab-monitor'

    # Load and evaluate rules in this file every 'evaluation_interval' seconds.
            rule_files:
                # - "first.rules"
                # - "second.rules"

    # A scrape configuration containing exactly one endpoint to scrape:
    # Here it's Prometheus itself.
            scrape_configs:
    # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
                - job_name: 'prometheus'

    # Override the global default and scrape targets from this job every 5 seconds.
                  scrape_interval: 5s
                  scrape_timeout: 10s

    # metrics_path defaults to '/metrics'
    # scheme defaults to 'http'.

                  target_groups:
                    - targets: ['localhost:8090']
```

- Now you can start prometheus server using the following command

```

    ./prometheus -config.file=prometheus.yml

```

Prometheus by default listens on port 9090


Promdash
--------
Steps to install Promdash

- Install git using the command "sudo apt-get install -y git"
- git clone https://github.com/prometheus/promdash
- In the root promdash directory run the command **cp config/database.yml.example config/database.yml**
- Configure database.yml "production tag" with host, username and password. Set the database tag to "galaxia".
- Set the following environment variables, substitute the values for username, password & host

.. code-block::

    export DATABASE_URL="mysql2://username:password@host/galaxia"
    export RAILS_ENV="production"

- Now install bundler using the command "sudo apt-get install -y bundler"
- sudo apt-get install -y libpq-dev mysql-client libmysqlclient-dev libsqlite3-dev
- bundle install
- bundle exec rake db:setup - This will set up db tables required for promdash
- make build
- bin/env bin/bundle exec bin/thin -p 3000  start
  Promdash is listening on port 3000
- Launch the promdash page using the url http://localhost:3000 and add a new server, set the Uri as
  http://<ip_address>:9090 & Server type as prometheus.

Docker
------
Install docker using the link https://docs.docker.com/engine/installation/linux/ubuntulinux/

cadvisor
--------
cadvisor is being used as a metrics exporter here, we use a docker image here
- Download the cadvisor image from https://hub.docker.com/r/google/cadvisor/
- Start cadvisor using the following command

```

     sudo docker run --volume=/:/rootfs:ro --volume=/var/run:/var/run:rw --volume=/sys:/sys:ro --volume=/var/lib/docker/:/var/lib/docker:ro  --publish=8090:8080   --detach=true
     --name=cadvisor google/cadvisor
```

Galaxia
-------
Steps to install Galaxia

- Download the source from <github_url>
- Install MySQL Driver for python

```

    sudo apt-get -y build-dep python-mysqldb
    sudo pip install MySQL-python
    sudo pip install -r requirements.txt
    sudo python setup.py install

```

- Run the tools/database.py as follows, here host is mysql host and username/password are for mysql

```

    python database.py --host localhost --type mysql --username root --password root**

```

This completes galaxia installation

Starting galaxia services
----------------------------
Galaxia comes up with following services gapi, grenderer and gexporter. Let us start them one by one
To test gexporter service you will need to setup OpenStack


    Run the following commands to start gapi service
    
    ```
     source openrc_example
     gapi --config-file etc/galaxia/galaxia.conf
  
    ```


    Run the following commands to start grenderer service
     
    ``` 
     source openrc_example
     grenderer --config-file etc/galaxia/galaxia.conf
    ```
    
    Run the following commands to start gexporter service
    
    ```
    source openrc_example
    gexporter --config-file etc/galaxia/galaxia.conf

    ```
Testing Galaxia Services
------------------------
Currently galaxia supports containers and hence we need to start some containers on the host to test galaxia services.
We will use httpd server(https://hub.docker.com/_/httpd/) images from docker hub for that

- start couple of httpd container

```    
sudo docker run --name sample_http -d  httpd
sudo docker run --name sample_http1 -d  httpd

```
- run some galaxia commands now
    
```
source openrc_example
galaxia --help
galaxia metrics list --type container
galaxia dashboard create --metrics-list container_memory_usage_bytes --names-list sample_http --name tes --unit-type docker
galaxia dashboard create --metrics-list container_memory_usage_bytes --search-string sample --search-type name --unit-type docker --name test1
```
- Using curl command
1) Create Dashboard

```
 http://localhost:7000/v1/gapi "PUT Request" with the following data
{"name": "ashish08" , "unit_type": "docker", "metrics_list": ["container_memory_usage_bytes", "container_cpu_system_seconds_total"], "names_list": ["httpd1_ecom1", "test123"]}
```

2) Update Dashboard
```
http://localhost:7000/v1/gapi "POST Request" with the following data
{"name": "ashish08" , "unit_type": "docker", "metrics_list": ["container_memory_usage_bytes", "container_cpu_system_seconds_total"], "names_list": ["httpd1_ecom1"]}
```
3) Delete Dashboard

```
http://localhost:7000/v1/gapi "DELETE Request" with the following data
{"name": "ashish08"}

```
4) Create Dashboard using search strings and type

```
http://localhost:7000/v1/gapi "PUT Request" with the following data
{"name": "ashish09" , "unit_type": "docker", "metrics_list": ["container_memory_usage_bytes", "container_cpu_system_seconds_total"], "search_string": "httpd", "search_type": "image"}

```

5) Catalogue API usage

```
http://localhost:7000/v1/catalogue?unit_type=container
http://localhost:7000/v1/catalogue?unit_type=dashboard
```

6) Metrics API usage

```
http://localhost:7000/v1/metrics?type=container
```

7) Exporter API usage

```
http://localhost:7000/v1/exporter
{"source_system": "prometheus", "target_system": "ceilometer", "metrics_list": ["cpu"], "time_interval": "1", "unit_type": "docker",  "exporter_name": "ashish2"}

```
### Contributing to Galaxia
-----------------------

- Galaxia uses github to manage our code, bugs, features. Pick up any bug and share your code fix with us using github pull requests.
- For any discussions or questions please reach us our mailing list @
- We are also available on our irc channel @

