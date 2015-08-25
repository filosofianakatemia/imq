import copy
import json
import sys
import uuid

question_page = {
    "children": [],
    "type": "page"
}

single_choise_grid_description = {
    "description": {
        "fi": "1: Ei lainkaan, 2: Melko vähän, " +
        "3: Vähän, 4: Jossain määrin, 5: Melko hyvin, " +
        "6: Hyvin, 7: Erittäin hyvin"
    },
    "idname": "section-separator",
    "title": {
        "fi": "Arvioi seuraavien väittämien paikkaansapitävyyttä työssäsi"
    },
    "type": "question"
}


def read_json_file(json_file_path):
    with open(json_file_path) as json_file:
        # TODO: check that file has content.
        return json.load(json_file)


def remove_question(id):
    for entry in company_survey_json_data["form"]:
        if "children" in entry:
            # http://stackoverflow.com/a/16143537
            # http://stackoverflow.com/a/9755790
            for child_entry in entry["children"]:
                if child_entry["id"] == id:
                    print("delete\t{0}\t\"{1}\"\n".
                          format(child_entry["id"],
                                 child_entry["title"]))
                    entry["children"].remove(child_entry)
                    break


def insert_question_after(id, question):
    for entry in company_survey_json_data["form"]:
        if "children" in entry:
            for index, child_entry in enumerate(entry["children"]):
                if child_entry["id"] == id:
                    print("insert\t{0}\t\"{1}\"\n"
                          "after\t{2}\t\"{3}\"\n"
                          "index\t{4}\n".
                          format(question["id"], question["title"],
                                 child_entry["id"], child_entry["title"],
                                 index + 1))
                    entry["children"].insert(index + 1, question)
                    break


def insert_question_before(id, question):
    for entry in company_survey_json_data["form"]:
        if "children" in entry:
            for index, child_entry in enumerate(entry["children"]):
                if child_entry["id"] == id:
                    print("insert\t{0}\t\"{1}\"\n"
                          "before\t{2}\t\"{3}\"\n"
                          "index\t{4}\n".
                          format(question["id"], question["title"],
                                 child_entry["id"], child_entry["title"],
                                 index))
                    entry["children"].insert(index, question)
                    break


def insert_frame_question_after(id, question):
    for entry in company_frame_json_data:
        if "children" in entry:
            for index, child_entry in enumerate(entry["children"]):
                if child_entry["id"] == id:
                    print("insert\t{0}\t\"{1}\"\n"
                          "after\t{2}\t\"{3}\"\n"
                          "index\t{4}\n".
                          format(question["id"], question["title"],
                                 child_entry["id"], child_entry["title"],
                                 index + 1))
                    entry["children"].insert(index + 1, question)
                    break


def paginate():
    QUESTIONS_IN_PAGE = 10
    for index, entry in enumerate(company_survey_json_data["form"]):

        single_choise_grid_description_copy = copy.deepcopy(
            single_choise_grid_description)
        single_choise_grid_description_copy["id"] = str(uuid.uuid1())
        company_survey_json_data["form"][index]["children"].insert(
            0, single_choise_grid_description_copy)

        if "children" in entry and len(entry["children"]) > QUESTIONS_IN_PAGE:
            question_page_copy = copy.deepcopy(question_page)
            company_survey_json_data["form"].append(question_page_copy)
            sliced_questions = entry["children"][QUESTIONS_IN_PAGE:]
            entry["children"] = entry["children"][:QUESTIONS_IN_PAGE]
            company_survey_json_data["form"][
                index + 1]["children"].extend(sliced_questions)


master_survey_json_flattened_file_path = "./master_latest_flattened.json"

company_name = sys.argv[1]
overlay_survey_json_file_path = "./{0}/overlay.json".format(company_name)

# Get flattened questions.
company_survey_json_data = read_json_file(
    master_survey_json_flattened_file_path)

overlay_survey_json_data = read_json_file(overlay_survey_json_file_path)

# Update main attributes.
company_survey_json_data["title"] = overlay_survey_json_data["title"]
# NOTE: Replace title attribute with name attribute
# if using FluidSurveys API v3.
# company_survey_json_data["name"] = overlay_survey_json_data["name"]
company_survey_json_data["IMQ_VERSION"] = company_survey_json_data["version"]
del company_survey_json_data["version"]

# http://stackoverflow.com/a/24898931
if "form" in overlay_survey_json_data:
    for i in overlay_survey_json_data["form"]:
        if "children" in i:
            for j in i["children"]:
                if "DELETE_ID" in j:
                    remove_question(j["DELETE_ID"])
                elif "BEFORE_ID" in j:
                    print("insert")
                    insert_question_before(j["BEFORE_ID"], j)
                elif "AFTER_ID" in j:
                    insert_question_after(j["AFTER_ID"], j)

paginate()

overlay_frame_json_file_path = "./{0}/overlay_frame.json".format(company_name)
overlay_frame_json_data = read_json_file(overlay_frame_json_file_path)

company_frame_json_data = read_json_file("./master_frame.json")

for entry in overlay_frame_json_data:
    if "children" in entry:
        for child_entry in entry["children"]:
            if "DELETE_ID" in child_entry:
                print("delete")
            elif "BEFORE_ID" in child_entry:
                print("before")
            elif "AFTER_ID" in child_entry:
                insert_frame_question_after(child_entry["AFTER_ID"],
                                            child_entry)

# Add survey frame. Last question goes to the end of the survey.
PREPENDING_QUESTIONS_IN_FRAME = len(company_frame_json_data) - 1
company_survey_json_data["form"] = company_frame_json_data[
    :PREPENDING_QUESTIONS_IN_FRAME] + company_survey_json_data[
    "form"] + company_frame_json_data[PREPENDING_QUESTIONS_IN_FRAME:]

# Uncomment for debugging.
# print(json.dumps(company_frame_json_data, indent=4, ensure_ascii=False))

with open("./{0}/survey.json".format(company_name), "w") as outfile:
    json.dump(company_survey_json_data, outfile, indent=2, ensure_ascii=False)
