import csv
import json
import os
import sys
import re
import requests
import time
from datetime import datetime
import query_info

SURVEY_DATA_BASE_PATH = "data"
QUESTIONS_BASE_PATH = "kysymykset"
TIMESTAMP = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")

def get_company_name_and_survey_name():
    survey_info = {}

    if len(sys.argv) < 2:
        survey_info = query_info.query_company_name_and_survey_name()
    else:
        survey_info["company_name"] = sys.argv[1]
        survey_info["survey_name"] = sys.argv[2]

    return survey_info


def read_json_file(json_file_path):
    with open(json_file_path) as json_file:
        # TODO: check that file has content.
        return json.load(json_file)


def get_survey_json_data(company_name, survey_name):
    survey_json_file_path = ("./{0}/{1}/{2}/survey.json"
                             .format(SURVEY_DATA_BASE_PATH,
                                     company_name,
                                     survey_name))
    return read_json_file(survey_json_file_path)

def get_survey_lang(survey_json_data):
    if "languages" in survey_json_data:
        for language in survey_json_data["languages"]:
            if language["isDefault"]:
                return language["code"]
    # default to fi if no default language found
    return "fi"

def get_credentials():
    credentials = {}
    if len(sys.argv) < 4:
        credentials = query_info.query_credentials()
    else:
        credentials["email"] = sys.argv[3]
        credentials["password"] = sys.argv[4]

    return credentials


def get_response(id, as_json):
    if as_json:
        get_response_url = (("https://fluidsurveys.com/"
                             "api/v2/surveys/{}/responses/?expand_GET"
                             ).format(id))

        get_survey_response = requests.get(get_response_url,
                                           auth=(email, password),
                                           headers=headers)
        if (get_survey_response.status_code == 200 or     # api v2
                get_survey_response.status_code == 201):  # api v3

            with open("./{0}/{1}/{2}/response.json"
                      .format(SURVEY_DATA_BASE_PATH, company_name,
                              survey_name),
                      "w") as outfile:
                json.dump(get_survey_response.json(), outfile, indent=2,
                          ensure_ascii=False)
            exit()
    else:
        # http://stackoverflow.com/a/53180
        get_response_url = (("https://fluidsurveys.com/api/v3/surveys/{}/csv/"
                             "?comma_separated=true&include_id=true"
                             "&show_titles=false")
                            .format(id))

    return requests.get(get_response_url,
                        auth=(email, password), headers=headers)


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
        if ("completed" not in row[j] and is_survey_question(row[j]) is False):
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

    # ID field needs to be added to spss responses
    if key_to_compare == "_id":
        return True

    if "avoin" in key_to_compare:
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


def create_response_files():
    # questions_version = survey_json_data["IMQ_VERSION"]

    # Get flattened questions.
    # master_survey_json_flattened_file_path = ("./{0}/{1}/"
    #                                           "master_flattened_{1}.json"
    #                                           .format(QUESTIONS_BASE_PATH,
    #                                                   questions_version))

    # flattened_master_survey_json_data = read_json_file(
    #     master_survey_json_flattened_file_path)

    yyyy_mm_dd = time.strftime("%Y_%m_%d")

    os.makedirs("./{0}/{1}/{2}/{3}/"
                .format(SURVEY_DATA_BASE_PATH, company_name, survey_name,
                        TIMESTAMP))

    # TODO: Add company name.
    full_responses = ("./{0}/{1}/{2}/{3}/full_responses_{4}.csv"
                      .format(SURVEY_DATA_BASE_PATH, company_name, survey_name,
                              TIMESTAMP, yyyy_mm_dd))
    spss_responses = ("./{0}/{1}/{2}/{3}/spss_responses_{4}.csv"
                      .format(SURVEY_DATA_BASE_PATH, company_name, survey_name,
                              TIMESTAMP, yyyy_mm_dd))

    return {"full": full_responses, "spss": spss_responses}


def generate_response_files():
    # http://stackoverflow.com/a/26209120
    get_survey_response.encoding = "utf8"
    # http://stackoverflow.com/a/16268214
    reader = csv.reader(get_survey_response.text.split("\n"))
    spss_question_ids = []

    response_files = create_response_files()

    # UTF-8 http://stackoverflow.com/a/5181085
    with open(response_files["full"], "w", newline="",
              encoding="utf8") as full_responses:
        # http://importpython.blogspot.fi/2009/12/how-to-get-todays-date-in-yyyymmdd.html
        full_responses_writer = csv.writer(full_responses, quotechar="'",
                                           quoting=csv.QUOTE_NONNUMERIC)
        with open(response_files["spss"], "w", newline="",
                  encoding="utf8") as spss_responses:
            spss_responses_writer = csv.writer(spss_responses, quotechar="'",
                                               quoting=csv.QUOTE_NONNUMERIC)
            reverse_questions = []
            for (i, row) in enumerate(reader):
                # Save raw response row to a file.
                full_responses_writer.writerow(row)
                row_filtered_columns = []

                if i == 0:
                    # key_to_compare_row = row
                    filtered_columns = columns_to_filter(row)
                    for (j, column) in enumerate(row):
                        if (j not in filtered_columns and
                                "completed" not in column):

                            key = column

                            if key.startswith("{"):
                                key = key[1:]
                            if key.startswith("_"):
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

    return {"spss_question_ids": spss_question_ids}


def generate_prepare_data_spss_syntax(question_ids):
    measurement_level = set_question_measurement_level_to_scale(question_ids)
    question_labels = set_question_labels(question_ids)
    dataset_name = rename_dataset()

    with open("./{0}/{1}/{2}/{3}/prepare_data.sps"
              .format(SURVEY_DATA_BASE_PATH, company_name, survey_name,
                      TIMESTAMP),
              "wt") as out_file:
        out_file.write(measurement_level + question_labels + dataset_name)


def set_question_measurement_level_to_scale(question_ids):
    measurement_level = "VARIABLE LEVEL\n"

    for question_id in question_ids:
        if not question_id.startswith("tt"):
            # NOTE: Background question IDs starts with "tt"
            # It could be better to check IDs against survey.json
            measurement_level += ("{}(SCALE)\n".format(question_id))
    measurement_level += ".\n"

    return measurement_level

def set_question_labels(question_ids):
    labels = "VARIABLE LABELS\n"

    for question_id in question_ids:
        labels += ("{} '{}'\n".format(question_id, get_title_for_question(question_id)))
    labels += ".\n"
    return labels


def get_title_for_question(question_id):
    # Resort to using the question_id as title if not found
    title = question_id
    for entry in survey_json_data["form"]:
        if "children" in entry:
            for child_entry in entry["children"]:
                if child_entry["id"] == question_id and "title" in child_entry:
                    if survey_lang in child_entry["title"]:
                        title = child_entry["title"][survey_lang]
                    break
    return title


def rename_dataset():
    # NOTE: Dataset name can't contain dash, use undescore.
    return "DATASET NAME {0}_{1}.".format("dataset", time.strftime('%Y%m%d'))


def generate_analysis_syntax(question_ids):
    formulas = generate_analysis_formulas_map()
    formulas_syntax = []

    if "SPSS_FORMULAS_ORDER" in survey_json_data:
        for order_entry in survey_json_data["SPSS_FORMULAS_ORDER"]:
            formula_found = False
            formula_type = order_entry["formula"]
            if formula_type in formulas:
                for formula in formulas[formula_type]:
                    if formula["id"] == order_entry["id"]:
                        formula_found = True
                        formula_syntax = generate_formula(formula,
                                                          formula_type,
                                                          False, question_ids)
                        formulas_syntax.append(formula_syntax)
            if not formula_found and "SPSS_SUM_FORMULAS" in survey_json_data:
                for formulas_entry in survey_json_data["SPSS_SUM_FORMULAS"]:
                    if (formulas_entry["id"] == order_entry["id"] and
                            formula_type in
                            formulas_entry["formulas"]):
                        formula_found = True
                        formula_data = {
                            "id": formulas_entry["id"],
                            "questions": formulas_entry["children"]
                        }
                        formula_syntax = generate_formula(formula_data,
                                                          formula_type, True,
                                                          question_ids)
                        formulas_syntax.append(formula_syntax)

    return "\n\n".join(formulas_syntax) + "\n"


def generate_analysis_formulas_map():
    formulas = {}
    for entry in survey_json_data["form"]:
        if "children" in entry:
            for child_entry in entry["children"]:
                if "SPSS_FORMULAS" in child_entry:
                    for question_formula_entry in child_entry["SPSS_FORMULAS"]:
                        formula_name = question_formula_entry["name"]
                        if formula_name not in formulas:
                            formulas[formula_name] = []
                        for formula_id in question_formula_entry["ids"]:
                            formula_id_found = False
                            for entry in formulas[formula_name]:
                                if entry["id"] == formula_id:
                                    formula_id_found = True
                                    entry["questions"].append(child_entry[
                                                              "id"])
                            if not formula_id_found:
                                formulas[formula_name].append({
                                    "id": formula_id,
                                    "questions": [child_entry["id"]]
                                })
    return formulas


def generate_formula(formula, formula_type, sum_formula, question_ids):
    if formula_type == "average":
        return generate_average_formula(formula["id"], formula["questions"])
    elif formula_type == "reliability":
        return generate_reliability_formula(formula["id"],
                                            formula["questions"])
    elif formula_type == "frequency":
        return generate_frequency_formula(formula["questions"], sum_formula)
    elif formula_type == "means":
        return generate_means_formula(formula["questions"], sum_formula,
                                      question_ids)
    elif formula_type == "correlations":
        return generate_correlations_formula(formula["questions"])


def generate_average_formula(formula_id, question_ids):
    mean = "COMPUTE {}=(\n".format(formula_id)
    mean += "+\n".join(question_ids)
    mean += "\n)/{}.".format(len(question_ids))
    mean += "\nEXECUTE."
    return mean


def generate_reliability_formula(formula_id, question_ids):
    reliability = "RELIABILITY"
    reliability += "\n/VARIABLES=\n"
    reliability += "\n".join(question_ids)
    reliability += "\n/SCALE('ALL VARIABLES') ALL"
    reliability += "\n/MODEL=ALPHA."
    return reliability


def generate_frequency_formula(question_ids, sum_formula):
    frequency = "FREQUENCIES"
    frequency += "\n/VARIABLES=\n"
    frequency += "\n".join(question_ids)
    if sum_formula:
        frequency += "\n/NTILES=4"
        frequency += "\n/STATISTICS=STDDEV MEAN"
        frequency += "\n/HISTOGRAM NORMAL"
    frequency += "\n/ORDER=ANALYSIS."
    return frequency


def generate_means_formula(variable_ids, sum_formula, question_ids):
    means = "MEANS TABLES=\n"
    means += "\n".join(variable_ids)
    if (sum_formula and
            ("tt1" in question_ids or
             "tt2" in question_ids or
             "tt3" in question_ids)):
        means += "\nBY"
        if "tt1" in question_ids:
            means += " tt1"
        if "tt2" in question_ids:
            means += " tt2"
        if "tt3" in question_ids:
            means += " tt3"
    means += "\n/CELLS MEAN COUNT STDDEV."
    return means


def generate_correlations_formula(variable_ids):
    correlations = "CORRELATIONS"
    correlations += "\n/VARIABLES=\n"
    correlations += "\n".join(variable_ids)
    correlations += "\n/PRINT=TWOTAIL NOSIG"
    correlations += "\n/MISSING=PAIRWISE."
    return correlations


def save_analysis_syntax(syntax):
    with open("./{0}/{1}/{2}/{3}/analysis.sps"
              .format(SURVEY_DATA_BASE_PATH, company_name, survey_name,
                      TIMESTAMP),
              "wt") as out_file:
        out_file.write(syntax)

survey_info = get_company_name_and_survey_name()
company_name = survey_info["company_name"]
survey_name = survey_info["survey_name"]
# Get questions, or call get_survey with survey_id.
survey_json_data = get_survey_json_data(company_name, survey_name)
survey_id = survey_json_data["id"]
survey_lang = get_survey_lang(survey_json_data)
credentials = get_credentials()
email = credentials["email"]
password = credentials["password"]
headers = {"Accept": "application/json"}
response_as_json = False
print("Haetaan kyselyä id:llä {}".format(survey_id))
get_survey_response = get_response(survey_id, response_as_json)
if get_survey_response.status_code == 200:
    print("Kysely löytyi. Tallennetaan kysely ja luodaan vastauksista "
          "tiedosto analyysia (SPSS/PSPP) varten.")
    response_data = generate_response_files()
    print("Kysely tallennettu ja tiedosto luotu.")
    print("Luodaan dataa valmisteleva syntaksitiedosto.")
    generate_prepare_data_spss_syntax(response_data["spss_question_ids"])
    print("Dataa valmisteleva syntaksitiedosto luotu.")
    print("Luodaan analyysin syntaksitiedosto.")
    analysis_syntax = generate_analysis_syntax(response_data[
                                               "spss_question_ids"])
    save_analysis_syntax(analysis_syntax)
    print("Analyysin syntaksitiedosto luotu.")
    print("Vastausten hakeminen valmis. Tiedostot luotu kansioon "
          "{0}/{1}/{2}/{3}/{4}/".format(os.getcwd(),
                                        SURVEY_DATA_BASE_PATH,
                                        company_name,
                                        survey_name,
                                        TIMESTAMP))
else:
    print("Kyselyä ei löytynyt. Yritä uudelleen.")
    exit()
