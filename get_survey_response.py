import getpass
import json
import sys
import re
import requests
# import get_survey

response_id = sys.argv[1]


def read_json_file(json_file_path):
    with open(json_file_path) as json_file:
        # TODO: check that file has content.
        return json.load(json_file)

email = input('Email: ')
password = getpass.getpass()
headers = {"Accept": "application/json"}

# http://stackoverflow.com/a/53180
get_response_url = ("https://fluidsurveys.com/api/v3/surveys/{0}/responses/".
                    format(response_id))

get_survey_response = requests.get(get_response_url,
                                   auth=(email, password), headers=headers)

# Get questions.
survey_json_file_path = "./survey.json"
# Or call get_survey with response_id
survey_json_data = read_json_file(survey_json_file_path)

# Get flattened questions.
master_survey_json_flattened_file_path = "../master_latest_flattened.json"
flattened_master_survey_json_data = read_json_file(
    master_survey_json_flattened_file_path)

if survey_json_data["IMQ_VERSION"] == flattened_master_survey_json_data[
        "version"]:
        # Can use the latest :)
    pass
else:
    # TODO: Use something else :O
    print("No good")


# http://stackoverflow.com/a/18516125
def valid_uuid(uuid):
    regex = re.compile(
        '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z',
        re.I)
    match = regex.match(uuid)
    return bool(match)


def is_survey_question_filter(response):
    filtered_response = {}
    for key in response:
        key_to_compare = key
        if "avoin" in key_to_compare:
            pass
        elif key_to_compare.startswith("tt"):
            # id starting with tt is not a question
            pass
        else:
            if key_to_compare.endswith("_0"):
                # FluidSurveys adds a suffix to the ids. Remove it!
                key_to_compare = key_to_compare[:-2]
            for entry in survey_json_data["form"]:
                if "children" in entry:
                    for child_entry in entry["children"]:
                        if (child_entry["id"] == key_to_compare
                                and not valid_uuid(key_to_compare)):
                            # Is a question. UUIDs are used for other purposes.
                            filtered_response[key_to_compare] = response[key]

    return filtered_response

if get_survey_response.status_code == 200:
    results = []
    response_json_data = get_survey_response.json()
    # TODO: Save response to a file.
    if "results" in response_json_data:
        for entry in response_json_data["results"]:
            if entry["_completed"] == 0:
                # FIXME: filter uncompleted, not completed
                results.append(is_survey_question_filter(entry))

    print(json.dumps(results, indent=4, sort_keys=True))
else:
    print("Request failed")
