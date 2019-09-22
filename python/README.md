Doc à mettre à jour

# Djoro regulation server

## Development environment

### Setup virtualenv
I strongly recommend using virtualenv to create customized python environment for development.
Tutorial here: http://simononsoftware.com/virtualenv-tutorial/

### Run the tests

    (virt)-> nosetests -s -v

### Run the regulation server

Default configuration :
 * mongodb instance set to *localhost:27017* and the *ecocoon-dev* database.
 * restful service starts on *localhost:5000*
You can change these settings in the bin/ecocoon_regulation script itself if needed.

Before launching the service you have to build it in develop mode from the ecocoon-regulation directory:

    (virt)-> python setup.py develop

Then Launch the restful regulation backend by running the following command :

    (virt)-> bin/djoro-regulation-server.py


### Query the regulation service using curl

* **launch recommendations for all users:**

        curl -X GET http://localhost:5000/sites/:siteId

    It should reply the following if all recommendations was done successfully:

        {
            "status": "ok"
        }



## Prod mode

### install the ecocoon-regulation library with easy_install
From the parent directory of this project, run the easy_install command to install the ecocoon-regulation library to the virtual environment.
Don't forget to activate the virtual environment before:

    (virt)-> sudo easy_install ecocoon-regulation

### launching the service in background

It is practical to launch the regulation service using **forever** utility.
To do so launch the server with the following command:

    $ forever start -c python ecocoon-regulation

Once started, use forever command line to locate log file:

    (ecocoon)➜  ecocoon ✗ forever list
        info:    Forever processes running
        data:        uid  command script                                    forever pid   logfile                       uptime
        data:    [0] OikN python  ecocoon-regulation/bin/ecocoon-regulation 73428   73436 /Users/ivan/.forever/OikN.log 0:0:0:1.936
