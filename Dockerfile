FROM python:3.5.2
MAINTAINER Open Semantics Group <osemantics@gmail.com>

# update old version
RUN pip list --local --outdated --format=freeze | cut -d= -f 1 | xargs -n1 pip install -U

WORKDIR /app
ADD requirements.txt /app/

# Project requirements
RUN pip install -r requirements.txt
# .. plus some NLTK corpora
RUN python -m nltk.downloader names punkt

# Deployment requirements
RUN pip install 'uwsgi==2.0.14'

# finally add application
ADD src/ /app/

# Go!
CMD [ "uwsgi", "--ini", "uwsgi.ini" ]