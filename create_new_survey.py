# https://gist.github.com/rmoff/9474035#file-fs_example-py-L35-L46

import getpass
import json
import sys
import requests

new_survey_path = sys.argv[1]

with open(new_survey_path) as survey_json_file:
    survey_json_data = json.load(survey_json_file)
    # Serializing is needed.
    survey_json_data_serialized = json.dumps(survey_json_data)

email = input('Email: ')
password = getpass.getpass()
headers = {"Content-Type": "application/json"}
# NOTE: v3 does not work for some reason
url = "https://fluidsurveys.com/api/v2/surveys/"

new_survey_response = requests.post(url, auth=(email, password),
                                    data=survey_json_data_serialized,
                                    headers=headers)

if (new_survey_response.status_code == 200 or     # api v2
        new_survey_response.status_code == 201):  # api v3
    # http://docs.python-requests.org/en/latest/user/quickstart/#more-complicated-post-requests
    print("Survey created!")
    new_survey_response_json = new_survey_response.json()
    # Update id into survey.
    survey_json_data["id"] = new_survey_response_json["id"]
    with open(new_survey_path, "w") as outfile:
        json.dump(survey_json_data, outfile, indent=2, ensure_ascii=False)
else:
    print("Request failed")
