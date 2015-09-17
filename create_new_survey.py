# https://gist.github.com/rmoff/9474035#file-fs_example-py-L35-L46

import getpass
import json
import requests


def create_survey(survey_json_data, *args, **kwargs):
    credentials = kwargs.get('credentials', None)
    if not credentials:
        email = input('Email: ')
        password = getpass.getpass()
    else:
        email = credentials["email"]
        password = credentials["password"]

    new_survey_response = do_create_survey(survey_json_data, email, password)
    if (new_survey_response.status_code == 200 or     # api v2
            new_survey_response.status_code == 201):  # api v3
        return new_survey_response.json()

    else:
        print(new_survey_response.status_code)
        return None


def do_create_survey(survey_json_data, email, password):
    headers = {"Content-Type": "application/json"}
    # NOTE: v3 does not work for some reason
    url = "https://fluidsurveys.com/api/v2/surveys/"
    survey_json_data_serialized = json.dumps(survey_json_data)
    return requests.post(url, auth=(email, password),
                         data=survey_json_data_serialized, headers=headers)
