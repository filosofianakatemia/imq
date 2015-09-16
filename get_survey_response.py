import csv
import getpass
import json
import sys
import re
import requests
import time

response_id = sys.argv[1]


def read_json_file(json_file_path):
    with open(json_file_path) as json_file:
        # TODO: check that file has content.
        return json.load(json_file)

email = input('Email: ')
password = getpass.getpass()
headers = {"Accept": "application/json"}

# http://stackoverflow.com/a/53180
get_response_url = (("https://fluidsurveys.com/api/v3/surveys/{0}/csv/"
                     "?comma_separated=true&include_id=true&show_titles=false")
                    .format(response_id))

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
        "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z",
        re.I)
    match = regex.match(uuid)
    return bool(match)


def columns_to_filter(row):
    filtered_columns = []
    for j, entry in enumerate(row):
        if ("completed" not in row[j] and
                is_survey_question(row[j]) is False):
            filtered_columns.append(j)

    return filtered_columns


def is_completed(response):
    for entry in response:
        if "Incomplete" in response:
            return False

    return True


def is_survey_question(response_variable):
    key_to_compare = response_variable

    if key_to_compare.startswith("{"):
        key_to_compare = key_to_compare[1:]
    if key_to_compare.endswith("}"):
        key_to_compare = key_to_compare[:-1]

    if key_to_compare == "avoin":
        pass
    else:
        if key_to_compare.endswith("_0"):
            # FluidSurveys adds a suffix to the ids. Remove it!
            key_to_compare = key_to_compare[:-2]

        for entry in survey_json_data["form"]:
            if "children" in entry:
                for child_entry in entry["children"]:
                    if (key_to_compare in child_entry["id"]
                            and not valid_uuid(key_to_compare)):
                        # Is a question. UUIDs are used for other purposes.
                        return True

    return False


def is_reverse_question(question_id):
    for entry in survey_json_data["form"]:
        if "children" in entry:
            for child_entry in entry["children"]:
                if (question_id == child_entry["id"] and
                        "REVERSE_VALUE" in child_entry):
                    return True
    return False


def is_reverse_value(value_index, reverse_questions):
    for question in reverse_questions:
        if question["index"] == value_index:
            return True
    return False


def flip_value(value):
    if not value:
        # http://stackoverflow.com/a/9573283
        # There <i>should</i> be value since incompleted responses are removed.
        pass
    else:
        value = int(value)
        if value == 1:
            value = 7
        elif value == 2:
            value = 6
        elif value == 3:
            value = 5
        elif value == 5:
            value = 3
        elif value == 6:
            value = 2
        elif value == 7:
            value = 1
    return value


def is_float(value):
    # http://stackoverflow.com/a/20929983
    try:
        float(value)
        return True
    except:
        return False


def generate_prepare_data_spss_syntax(question_ids):
    measurement_level = set_question_measurement_level_to_scale(question_ids)
    dataset_name = rename_dataset()

    with open("prepare_data.sps", "wt") as out_file:
        out_file.write(measurement_level + dataset_name)


def set_question_measurement_level_to_scale(question_ids):
    measurement_level = "VARIABLE LEVEL\n"

    for question_id in question_ids:
        if not question_id.startswith("tt"):
            # NOTE: Background question IDs starts with "tt"
            # It could be better to check IDs against survey.json
            measurement_level += ("{}(SCALE)\n".format(question_id))
    measurement_level += ".\n"

    return measurement_level


def rename_dataset():
    # NOTE: Dataset name can't contain dash, use undescore.
    return "DATASET NAME {0}_{1}.".format("dataset", time.strftime('%Y%m%d'))


if get_survey_response.status_code == 200:
    # http://stackoverflow.com/a/26209120
    get_survey_response.encoding = "utf8"
    # http://stackoverflow.com/a/16268214
    reader = csv.reader(get_survey_response.text.split("\n"))
    timestamp = time.strftime('%Y-%m-%d')

    # TODO: Add company name.
    full_responses = "full_responses-{0}.csv".format(timestamp)
    spss_responses = "spss_responses-{0}.csv".format(timestamp)
    spss_question_ids = []

    # UTF-8 http://stackoverflow.com/a/5181085
    with open(full_responses, "w", newline="",
              encoding="utf8") as full_responses:
        # http://importpython.blogspot.fi/2009/12/how-to-get-todays-date-in-yyyymmdd.html
        full_responses_writer = csv.writer(full_responses, quotechar="'",
                                           quoting=csv.QUOTE_NONNUMERIC)
        with open(spss_responses, "w", newline="",
                  encoding="utf8") as spss_responses:
            spss_responses_writer = csv.writer(spss_responses, quotechar="'",
                                               quoting=csv.QUOTE_NONNUMERIC)
            reverse_questions = []
            for (i, row) in enumerate(reader):
                # Save raw response row to a file.
                full_responses_writer.writerow(row)
                row_filtered_columns = []

                if i == 0:
                    key_to_compare_row = row
                    filtered_columns = columns_to_filter(row)
                    for (j, column) in enumerate(row):
                        if (j not in filtered_columns and
                                "completed" not in column):

                            key = column

                            if key.startswith("{"):
                                key = key[1:]
                            if key.endswith("}"):
                                key = key[:-1]
                            if key.endswith("_0"):
                                key = key[:-2]

                            if is_reverse_question(key):
                                reverse_questions.append({"question_id": key,
                                                          "index": j})
                            row_filtered_columns.append(key)
                            spss_question_ids.append(key)

                else:
                    if is_completed(row):
                        for (j, column) in enumerate(row):
                            if (j not in filtered_columns and
                                    "complete" not in column.lower()):
                                if is_reverse_value(j, reverse_questions):
                                    column = flip_value(column)
                                if is_float(column):
                                    column = int(column)
                                row_filtered_columns.append(column)
                spss_responses_writer.writerow(row_filtered_columns)

    generate_prepare_data_spss_syntax(spss_question_ids)
