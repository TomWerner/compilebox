## What is it? ##
This is a modified version of the original CompileBox (https://github.com/remoteinterview/compilebox).
This version of CompileBox uses Flask instead of NodeJS and includes instructions for deploying to EC2. This was
specifically modified for use with the University of Iowa's high school Hawkeye Programming Challenge.
Because the languages required are a subset of the original CompileBox, this version has been stripped down
to include only Java, Python, C++/C, C#, and Visual Basic.

## Why would you use it? ##
CompileBox is a *Docker* based sandbox to run untrusted code and return the output to your app.
Users can submit their code in any of the supported languages.
The system will test the code in an isolated environment.
This way you do not have to worry about untrusted code possibly damaging your server intentionally or unintentionally.
You can use this system to allow your users to compile their code right in the browser.

## How does it work? ##
A client will submit code in a given language with standard input to the API.
The API then creates a new *Docker* container and runs the code using the compiler/interpreter of that language.
The program runs inside a virtual machine with limited resources and has a time-limit for execution (20s by default).
Once the output is ready it is sent back to the client-side app.
The *Docker* container is destroyed and all the files are deleted from the server.

No two submissions have access to each other's *Docker* instances or files.


## Installation/Deployment Instructions ##

* Go to the 'Setup' directory.
    - Open the Terminal as root user
    
    - Execute the script **Install_*.sh**, select the file which best suites your Operating System description.
    This will install the Docker and NodeJs pre-requisites to your system and create an image called
    'virtual_machine' inside the Docker.
    DockerVM may take around 20 to 30 minutes depending on your internet connection.

    -  The CompileBox API has been installed and run successfully on the following platforms
        - Ubuntu 12.04 LTS
        - Ubuntu 13.10
        - Ubuntu 14.04 LTS
        - Linux Mint 15

* Go to the project root directory
    - Install pip (```sudo apt-get install python-pip python-dev build-essential``` on Ubuntu)

    - Install the project requirements (```sudo pip install -r requirements.txt```)

* Install Nginx
    - ```sudo apt-get install nginx``` on Ubuntu

    - Modify /etc/nginx/nginx.conf (Example)
```
worker_processes 1;

events {

    worker_connections 1024;

}

http {
    # Configuration for Nginx
    server {

        # Running port
        listen 80;

        # Proxy connections to the application servers
        # app_servers
        location / {

            proxy_pass         http://127.0.0.1:8000;
            proxy_redirect     off;
            proxy_set_header   Host $host;
            proxy_set_header   X-Real-IP $remote_addr;
            proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host $server_name;

        }
    }
}
```

* Start the API

    - ```sudo gunicorn app:app -D```
    This starts the app using gunicorn on 127.0.0.1:8000 (which nginx will re-route traffic to), and the -D
    flag makes it run as a daemon, so it will continue running after closing your ssh connection on EC2.

    
## Selecting The languages for Installation Inside Docker ##

The default Dockerfile installs the most used languages. To remove/change any, follow these steps

In order to select languages of your own choice you need to make 2 changes.<br>
    	1. <B>Dockerfile</B>: This file contains commands that you would normally give in your terminal to
    	 install that language. Add the required commands preceeded by the RUN keyword inside the Dockerfile.
    	 Run the "UpdateDocker.sh" script, present in the same folder if you are adding new language to already
    	 installed API, execute the Install_*.sh script otherwise,
    	 from your terminal after making the changes to your Dockerfile.<br>
        2. <B>app.py</B>: This file contains a list of compilers, ```compilerArray```.
        The compiler name, the source file name and the execution commands to Docker Container are taken from this file.
        Add the credentials of the language you are adding to this array.<br>

> Note: Additionally while setting up the API for the first time,
you can comment out those languages from the Dockerfile that you do not wish to install, since they can be added later.

## Adding Your Own Languages ##

In order to add your own languages you need to following steps.
<br>
1. <b>Modify the Dockerfile</b>: The Dockerfile is present in the Setup folder and contains the commands that you would
normally write in your terminal to install a particular language. Append the commands for the language of your
choice to the end of the Dockerfile.<br>
2. <b>Execute UpdateDocker.sh</b> and wait for your language to be installed inside the virtual machine. <br>
3. <b>Modify Compilers.js</b>: Compilers.js file is available in the API folder and contains the information needed by
app.js to compile a given source code inside Docker container. The file only consists of an array which is described in
detail inside the file. Add the credentials for your language to the Array.

> Note:  You should be connected to the Internet when you run UpdateDocker.sh
