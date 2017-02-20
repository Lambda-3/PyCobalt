FROM python:3.4.5
MAINTAINER Open Semantics Group <osemantics@gmail.com>

WORKDIR /root
ADD . ./

# Project requirements
RUN pip install -r requirements.txt
# .. plus some NLTK corpora
RUN python -m nltk.downloader names punkt
# Deployment requirements
RUN pip install 'uwsgi==2.0.14'

# Go!
CMD [ "uwsgi", "--ini", "uwsgi.ini" ]