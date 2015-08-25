# https://gist.github.com/rmoff/9474035#file-fs_example-py-L16-L32

import getpass
import json
import sys
import requests

survey_id = sys.argv[1]

email = "imq@filosofianakatemia.fi"
password = getpass.getpass()
headers = {"Accept": "application/json"}

# http://stackoverflow.com/a/53180
get_survey_url = "https://fluidsurveys.com/api/v2/surveys/%s/?structure" % \
  survey_id

get_survey_response = requests.get(get_survey_url,
                                   auth=(email, password), headers=headers)
if get_survey_response.status_code == 200:
    # http://stackoverflow.com/a/12944035
    survey_json = json.loads(get_survey_response.text)
    print(json.dumps(survey_json, indent=4, sort_keys=True))

else:
    print("Request failed")
