# https://gist.github.com/rmoff/9474035#file-fs_example-py-L16-L32

import getpass
import json
import requests

email = "imq@filosofianakatemia.fi"
password = getpass.getpass()
headers = {"Accept": "application/json"}

# List all surveys
get_list_surveys_url = "https://fluidsurveys.com/api/v3/surveys/?page_size=100"


def list_surveys(url):
    list_surveys_response = get_list_surveys(url)
    handle_list_surveys_response(list_surveys_response)
    if has_next(list_surveys_response):
        count = json.loads(list_surveys_response.text)
        list_surveys(count["next"])
    return


def get_list_surveys(url):
    response = requests.get(url, auth=(email, password), headers=headers)
    return response


def handle_list_surveys_response(surveys_response):
    if surveys_response.status_code == 200:
        # http://stackoverflow.com/a/22360049
        # http://stackoverflow.com/a/16877439
        surveys = json.loads(surveys_response.text)["results"]
        global surveys_string  # http://stackoverflow.com/a/10588342
        for survey in surveys:
            surveys_string += "\tSurvey %s (id: %s)\n" % (survey["name"],
                                                          survey["id"])
    else:
        print("Request failed %s" % surveys_response.status_code)
    return surveys_string


def has_next(response):
    count = json.loads(response.text)
    if count["next"]:
        return True

surveys_string = ""
list_surveys(get_list_surveys_url)
print(surveys_string)
