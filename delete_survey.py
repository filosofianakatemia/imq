# https://gist.github.com/rmoff/9474035#file-fs_example-py-L35-L46

import getpass
import sys
import requests

email = "imq@filosofianakatemia.fi"
pw = getpass.getpass()
# http://www.tutorialspoint.com/python/python_command_line_arguments.htm
survey_id = str(sys.argv[1])
url = "https://fluidsurveys.com/api/v3/surveys/%s/" % survey_id

# TODO: Get status and delete only when not live.

new_surveyr = requests.delete(url, auth=(email, pw))

if (new_surveyr.status_code == 200):
    print("Survey is now deleted")
else:
    print("Request failed")
