FROM python:3.6.0
MAINTAINER Open Semantics Group <osemantics@gmail.com>

# update old version
RUN pip list --local --outdated --format=freeze | cut -d= -f 1 | xargs -n1 pip install -U && \
    pip install 'uwsgi==2.0.14'

# add application
ADD . /app/
WORKDIR /app
# Project requirements
RUN pip install -r requirements.txt \
    && python -m nltk.downloader names punkt
RUN python setup.py install

# Go!
CMD [ "uwsgi", "--ini", "uwsgi.ini" ]
