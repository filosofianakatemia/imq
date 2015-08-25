# https://gist.github.com/rmoff/9474035#file-fs_example-py-L35-L46

import getpass
import json
import sys
import requests

new_survey_path = sys.argv[1]

with open(new_survey_path) as survey_json_file:
    # Serializing is needed.
    survey_json_data_serialized = json.dumps(json.load(survey_json_file))

email = "imq@filosofianakatemia.fi"
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
    new_survey_response_json_data = json.loads(new_survey_response.text)
    print("Survey created!")
else:
    print("Request failed")
