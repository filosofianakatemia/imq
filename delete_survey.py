import getpass
import sys
import requests

email = input('Email: ')
password = getpass.getpass()
# http://www.tutorialspoint.com/python/python_command_line_arguments.htm
survey_id = str(sys.argv[1])
url = "https://fluidsurveys.com/api/v3/surveys/{0}/".format(survey_id)

# TODO: Get status and delete only when not live.

delete_survey_response = requests.delete(url, auth=(email, password))

if (delete_survey_response.status_code == 200):
    print("Survey is now deleted")
else:
    print("Request failed")
