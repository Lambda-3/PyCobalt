FROM python:3.6.1
MAINTAINER Open Semantics Group <osemantics@gmail.com>

# Install server requirement
RUN pip install 'uwsgi==2.0.15'

# add application
ADD . /app/
WORKDIR /app
# Project requirements
RUN pip install -r requirements.txt \
    && python -m nltk.downloader names punkt
RUN python setup.py install

# Go!
CMD [ "uwsgi", "--ini", "uwsgi.ini" ]
