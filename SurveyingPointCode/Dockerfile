FROM python:3.7-alpine

## make a local directory
RUN mkdir /SurveyingPointCode

# set "counter_app" as the working directory from which CMD, RUN, ADD references
WORKDIR /SurveyingPointCode

# now copy all the files in this directory to /counter_app
ADD . .

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install -r requirements.txt

# Listen to port 5000 at runtime
EXPOSE 5000

# Define our command to be run when launching the container
# Only is flask script is used

ENV FLASK_APP=surveyingpointcode.py

CMD ["flask", "run", "--host=0.0.0.0"]
