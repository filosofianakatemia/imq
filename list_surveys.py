# https://gist.github.com/rmoff/9474035#file-fs_example-py-L16-L32

import getpass
import json
import requests

# List all surveys
get_list_surveys_url = "https://fluidsurveys.com/api/v3/surveys/?page_size=100"
surveys = []


def get_surveys_and_print():
    surveys = get_surveys()
    for survey in surveys:
        print("{0}\t{1}".format(survey["id"], survey["name"]))


def get_surveys(*args, **kwargs):
    email = kwargs.get('email', None)
    password = kwargs.get('password', None)
    if not email:
        email = input('Email: ')
    if not password:
        password = getpass.getpass()
    headers = {"Accept": "application/json"}

    list_surveys(get_list_surveys_url, email, password, headers)
    return surveys


def list_surveys(url, email, password, headers):
    list_surveys_response = get_list_surveys(url, email, password, headers)
    handle_list_surveys_response(list_surveys_response)
    if has_next(list_surveys_response):
        count = json.loads(list_surveys_response.text)
        list_surveys(count["next"])
    return


def get_list_surveys(url, email, password, headers):
    response = requests.get(url, auth=(email, password), headers=headers)
    return response


def handle_list_surveys_response(surveys_response):
    if surveys_response.status_code == 200:
        # http://stackoverflow.com/a/22360049
        # http://stackoverflow.com/a/16877439
        surveys_json = json.loads(surveys_response.text)["results"]
        for survey in surveys_json:
            surveys.append({"name": survey["name"], "id": survey["id"]})
    else:
        print("Request failed {0}".format(surveys_response.status_code))
    return surveys


def has_next(response):
    count = json.loads(response.text)
    if count["next"]:
        return True
