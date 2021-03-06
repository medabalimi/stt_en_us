# stt_en_us
Speech to Text microservice for EN-US using Nvidia's Nemo models. Uses Celery to handle the requests asynchronously. Please note that the models themselves aren't a part of this repo. Nemo models are downloaded when you build the docker. By building the docker, it is assumed that you accept the license terms for the models as described in https://ngc.nvidia.com/legal/terms
Models used for 'best', 'good' and 'fast' are from https://catalog.ngc.nvidia.com/orgs/nvidia/teams/nemo/models/stt_en_contextnet_1024, https://catalog.ngc.nvidia.com/orgs/nvidia/teams/nemo/models/stt_en_contextnet_512 and https://catalog.ngc.nvidia.com/orgs/nvidia/teams/nemo/models/stt_en_contextnet_256 respectively. Refer to these links for the WER rates.

## Docker build instructions:
### Clone the git repo:
```shell
git clone https://github.com/medabalimi/stt_en_us.git
```
### Build docker container:
```shell
cd stt_en_us
docker build -t stt_en_us . 
```
### Running the docker
Mount a local folder for the container to store persistant data. 
Celery uses sqlite db to store the result set. 
All log files and temporary files are also written to the mounted folder
```shell
docker run -v `pwd`/mount:/opt/stt/mount -p 5000:5000 --shm-size=4096m -it stt_en_us
```

### Converting speech to text using the provided docker
The microservice contains 3 endpoints
1. /stt/{model_type}.
   {model_type} is one of ['best', 'good', 'fast']. 'best' provides best quality asr but takes more cpu time to process.
   'good' is faster and slightly higher WER than 'best'. 'fast' is the fastest and also highest WER among the 3.
    Returns a JSON which has the URL where the status/STT output of the submitted task can be obtained.
2. /tasks
   Return a task ids of all submitted tasks
3. /status/{task_id}
   Returns the status and/or STT output of a submitted task

Refer to the swagger docs at http://localhost:5000/apidocs/ 

