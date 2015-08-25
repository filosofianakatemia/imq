# https://gist.github.com/rmoff/9474035#file-fs_example-py-L35-L46

import getpass
import json
import sys
import requests

survey_id = sys.argv[1]
survey_path = sys.argv[2]  # TODO: relative path
# NOTE: Only title is editable.

# http://stackoverflow.com/a/2835672
with open(survey_path) as survey_json_file:
    # Serializing is needed.
    survey_json_data_serialized = json.dumps(json.load(survey_json_file))
    print(survey_json_data_serialized)

email = "imq@filosofianakatemia.fi"
password = getpass.getpass()
# headers = {'Accept': 'application/json'}
headers = {"Content-Type": "application/json"}
edit_survey_url = "https://fluidsurveys.com/api/v3/surveys/%s/" % survey_id

put_edit_survey_response = requests.put(edit_survey_url,
                                        auth=(email, password),
                                        headers=headers,
                                        data=survey_json_data_serialized)

if put_edit_survey_response.status_code == 200:
    # http://docs.python-requests.org/en/latest/user/quickstart/#more-complicated-post-requests
    # print(put_edit_survey_response.content)
    edit_survey_response_json_data = json.loads(put_edit_survey_response.text)
    print(json.dumps(edit_survey_response_json_data, indent=4, sort_keys=True))
else:
    print("Request failed %s" % put_edit_survey_response.status_code)
