# https://gist.github.com/rmoff/9474035#file-fs_example-py-L16-L32

import getpass
import json
import sys
import requests


def get_survey(*args, **kwargs):
    email = kwargs.get("email", None)
    password = kwargs.get("password", None)
    if not email:
        email = input("Email: ")
    if not password:
        password = getpass.getpass()

    survey_id = kwargs.get("id", None)
    if not survey_id:
        survey_id = sys.argv[1]

    details = kwargs.get("details", None)

    if not details:
        get_survey_url = "https://fluidsurveys.com/api/v2/surveys/{}/".format(
            survey_id)
    else:
        get_survey_url = ("https://fluidsurveys.com/api/v2/surveys/{}/"
                          "?structure").format(survey_id)

    headers = {"Accept": "application/json"}

    get_survey_details = requests.get(get_survey_url,
                                      auth=(email, password), headers=headers)
    if get_survey_details.status_code == 200:
        # http://stackoverflow.com/a/12944035
        survey_json = json.loads(get_survey_details.text)
        print_survey = kwargs.get("print", None)
        if not print_survey:
            return survey_json
        else:
            print(json.dumps(survey_json, indent=4, sort_keys=True))

    else:
        print("Request failed")
