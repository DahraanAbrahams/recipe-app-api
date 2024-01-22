FROM python:3.9-alpine3.13
LABEL maintainer="dahraanabrahams"

#Below command is recommended when using Python with Docker. Tells Python that we don't want to buffer the output
#All output from Pythn will be printed directly to console - i.e. we can see logs immediately
ENV PYTHONUNBUFFERED 1  

#below command copies local requirements.txt to the docker image. We can then use that to install the Python requirements
COPY ./requirements.txt ./tmp/requirements.txt 
COPY ./requirements.dev.txt ./tmp/requirements.dev.txt 
COPY ./app /app
#below command default directory where all commands are going to be run from when running commands on Docker image  
#basically setting it to the location where our Django project is going to be synced to so there's no need to specify full
#path when running command of the Django management command. It will automaticaly be run from /app   
WORKDIR /app
#below command we want to expose port 8000 from our container to our machine when we run the container. Allows us to access 
#that port on the container thats running from our image. This way we can connect to the Django Dev server
EXPOSE 8000

#below command defines a build argument called DEV and sets default value to false. We overriding this in docker-compose file
ARG DEV=false

#Below command runs the command on the alpine image that we're using when we build our image
#We could specify each command with it's own run however this creates a new image layer for each command. The idea is to keep
#the image as lighweight as possible. Thus we use one RUN command and seperate the different commands with && and \ 
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

#python -m venv /py && -> creates new venv where we'll store all of our dependencies
#/py/bin/pip install --upgrade pip && -> upgrades pip for the venv that we created
#/py/bin/pip install -r /tmp/requirements.txt && -> installs our requirements file(one we COPY over) inside the docker image. 
#rm -rf /tmp && -> we remove the /tmp folder because we don't want any extra dependencies on our image once we've created it. 
#adduser -> command to add new user inside of our image because its best practice not to use the root user which is the
#default user inside of the alpine image, which has full access to everything inside the image
#--disable-password -> don't want to add password to login
#--no-create-home -> don't create home for the user
#django-user -> we specify the name of the user

#Below command updates the environment variable inside of the image, i.e. the PATH env variable. This is included in all Linux
#OS and defines all directories where executables can be run 
ENV PATH="/py/bin:$PATH"

#Below command should be the final line of a Dockerfile and specifies the USER that we'll be switching to. Until this line, 
#eveything above is being run as the root user. The containers that are made out of this image will be run using the last USER
#that the image switched too. 
USER django-user