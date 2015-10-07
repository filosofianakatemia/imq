import sys
import requests
import get_survey
import query_info

credentials = query_info.query_credentials()
email = credentials["email"]
password = credentials["password"]
# http://www.tutorialspoint.com/python/python_command_line_arguments.htm
survey_id = str(sys.argv[1])
print("Getting survey details")
survey_json = get_survey.get_survey(email=email, password=password,
                                    id=survey_id)


def query_create_new_survey(survey_title):
    return input(("Do you want to delete survey \"{0}\"? (y) ")
                 .format(survey_title)).lower() == "y"

if survey_json and query_create_new_survey(survey_json["title"]):
    print("Deleting survey")
    url = "https://fluidsurveys.com/api/v3/surveys/{}/".format(survey_id)

    # TODO: Get status and delete only when not live.
    delete_survey_response = requests.delete(url, auth=(email, password))

    if (delete_survey_response.status_code == 200):
        print("Survey is now deleted")
    else:
        print("Request failed")
else:
    exit()
