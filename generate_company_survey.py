import copy
import json
import os.path
import requests
import sys
import uuid
import query_info
import list_surveys

SURVEY_DATA_BASE_PATH = "data"
QUESTIONS_BASE_PATH = "kysymykset"

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
        "fi": "Arvioi seuraavien väittämien paikkansapitävyyttä työssäsi"
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
                    print("poista\t{0}\t\"{1}\"\n".
                          format(child_entry["id"],
                                 child_entry["title"]["fi"]))
                    entry["children"].remove(child_entry)
                    break


def insert_question_before(id, question):
    for entry in company_survey_json_data["form"]:
        if "children" in entry:
            for index, child_entry in enumerate(entry["children"]):
                if child_entry["id"] == id:
                    print("lisää\t{0}\t\"{1}\"\n"
                          "ennen\t{2}\t\"{3}\"\n"
                          "indeksi\t{4}\n".
                          format(question["id"], question["title"]["fi"],
                                 child_entry["id"], child_entry["title"]["fi"],
                                 index))
                    entry["children"].insert(index, question)
                    break


def insert_question_after(id, question):
    for entry in company_survey_json_data["form"]:
        if "children" in entry:
            for index, child_entry in enumerate(entry["children"]):
                if child_entry["id"] == id:
                    print("lisää\t{0}\t\"{1}\"\n"
                          "jälkeen\t{2}\t\"{3}\"\n"
                          "indeksi\t{4}\n".
                          format(question["id"], question["title"]["fi"],
                                 child_entry["id"], child_entry["title"]["fi"],
                                 index + 1))
                    entry["children"].insert(index + 1, question)
                    break


def rename_question(id, question):
    for entry in company_survey_json_data["form"]:
        if "children" in entry:
            for index, child_entry in enumerate(entry["children"]):
                if child_entry["id"] == id:
                    print("nimettiin\t{0}\t\"{1}\"\n"
                          "uudelleen\t\t\"{2}\""
                          .format(child_entry["id"],
                                  child_entry["title"]["fi"],
                                  question["title"]["fi"]))
                    child_entry["title"] = question["title"]
                    break


def insert_frame_question_after(id, question):
    for entry in company_frame_json_data:
        if "children" in entry:
            for index, child_entry in enumerate(entry["children"]):
                if child_entry["id"] == id:
                    print("lisää\t{0}\t\"{1}\"\n"
                          "jälkeen\t{2}\t\"{3}\"\n"
                          "indeksi\t{4}\n".
                          format(question["id"], question["title"]["fi"],
                                 child_entry["id"], child_entry["title"]["fi"],
                                 index + 1))
                    entry["children"].insert(index + 1, question)
                    break


def validate_overlay_question_ids():
    # add default question ids to list
    overlay_question_ids = []
    overlay_question_affect_ids = []
    default_question_ids = []

    # FIXME: Any way to not assign these?
    message = ""
    invalid_overlay = False
    # FIXME

    for entry in company_survey_json_data["form"]:
        if "children" in entry:
            for child_entry in entry["children"]:
                default_question_ids.append(child_entry["id"])

    if "form" in overlay_survey_json_data:
        for i in overlay_survey_json_data["form"]:
            if "children" in i:
                for index, question in enumerate(i["children"]):
                    if "id" not in question:
                        if ("DELETE_ID" not in question and
                                "RENAME_ID" not in question):
                            message = ("Kysymyksellä \"{0}\" ei ole id:tä"
                                       .format(question["title"]["fi"]))
                            invalid_overlay = True
                            break
                    else:
                        if question["id"] in default_question_ids:
                            message = ("Kysymys id:llä {0} on jo olemassa"
                                       .format(question["id"]))
                            invalid_overlay = True
                            break
                        elif question["id"] in overlay_question_ids:
                            message = ("Kysymys id:llä {0} on jo olemassa"
                                       .format(question["id"]))
                            invalid_overlay = True
                            break
                        else:
                            overlay_question_ids.append(question["id"])

                    affect_id_type = get_affect_id_type(question)
                    if not affect_id_type:
                        message = ("Kysymykselle {0} ei ole määritelty mitään "
                                   "seuraavista kentistä: DELETE_ID, "
                                   "BEFORE_ID, AFTER_ID, RENAME_ID".format(
                                      question["id"]))
                        invalid_overlay = True
                        break
                    elif (affect_id_type != "DELETE_ID" and
                          affect_id_type != "RENAME_ID" and
                          question[affect_id_type] == question["id"]):
                        message = ("Kysymyksen id {0} on sama kuin kysymyksen "
                                   "kenttä {1}".format(question["id"],
                                                       affect_id_type))
                        invalid_overlay = True
                        break
                    else:
                        overlay_question_affect_ids.append(
                            question[affect_id_type])

    return {
        "message": message,
        "error": invalid_overlay
        }


def get_affect_id_type(overlay_question):
    if "DELETE_ID" in overlay_question:
        return "DELETE_ID"
    elif "BEFORE_ID" in overlay_question:
        return "BEFORE_ID"
    elif "AFTER_ID" in overlay_question:
        return "AFTER_ID"
    elif "RENAME_ID" in overlay_question:
        return "RENAME_ID"


def merge_overlay_questions():
    # http://stackoverflow.com/a/24898931
    if "form" in overlay_survey_json_data:
        for i in overlay_survey_json_data["form"]:
            if "children" in i:
                for j in i["children"]:
                    if "DELETE_ID" in j:
                        remove_question(j["DELETE_ID"])
                    elif "BEFORE_ID" in j:
                        insert_question_before(j["BEFORE_ID"], j)
                    elif "AFTER_ID" in j:
                        insert_question_after(j["AFTER_ID"], j)
                    elif "RENAME_ID" in j:
                        rename_question(j["RENAME_ID"], j)


def paginate_survey():
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


def get_company_name_and_survey_name():
    survey_info = {}

    if len(sys.argv) < 2:
        survey_info = query_info.query_company_name_and_survey_name()
    else:
        survey_info["company_name"] = sys.argv[1]
        survey_info["survey_name"] = sys.argv[2]

    return survey_info


def get_overlay_survey(company_name, survey_name):
    overlay_survey_json_file_path = "./{0}/{1}/{2}/overlay.json".format(
        SURVEY_DATA_BASE_PATH, company_name, survey_name)
    if os.path.isfile(overlay_survey_json_file_path):
        overlay_survey_json_data = (read_json_file(
                                    overlay_survey_json_file_path))
        return overlay_survey_json_data


def get_credentials():
    credentials = {}
    if len(sys.argv) < 4:
        credentials = query_info.query_credentials()
    else:
        credentials["email"] = sys.argv[3]
        credentials["password"] = sys.argv[4]

    return credentials


def get_existing_surveys(credentials):
    return list_surveys.get_surveys(email=credentials["email"],
                                    password=credentials["password"])


def is_existing_survey(company_name, survey_name, surveys):
    survey_name = "{0}-{1}".format(company_name, survey_name)
    for survey in surveys:
        if survey["name"] == survey_name:
            return True
    return False


# http://stackoverflow.com/a/973488
def get_latest_questions_version():
    return max(next(os.walk("./{}".format(QUESTIONS_BASE_PATH)))[1])


def get_flattened_questions():
    master_survey_json_flattened_file_path = (
        "./{0}/{1}/master_flattened_{1}.json".format(QUESTIONS_BASE_PATH,
                                                     questions_version))

    return read_json_file(master_survey_json_flattened_file_path)


def get_survey_frame():
    return read_json_file("./{0}/{1}/master_frame_{1}.json".format(
        QUESTIONS_BASE_PATH,
        questions_version))


def get_overlay_frame_and_merge_with_master():
    overlay_frame_json_file_path = ("./{0}/{1}/{2}/overlay_frame.json".format(
        SURVEY_DATA_BASE_PATH,
        company_name,
        survey_name))
    if os.path.isfile(overlay_frame_json_file_path):
        # Merge overlay frame with master.
        overlay_frame_json_data = read_json_file(overlay_frame_json_file_path)

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


def add_survey_frame():
    # Add survey frame. Last two questions goes to the end of the survey.
    PREPENDING_QUESTIONS_IN_FRAME = len(company_frame_json_data) - 2
    company_survey_json_data["form"] = company_frame_json_data[
        :PREPENDING_QUESTIONS_IN_FRAME] + company_survey_json_data[
        "form"] + company_frame_json_data[PREPENDING_QUESTIONS_IN_FRAME:]


def query_create_new_survey():
    return input("Lisää kysely FluidSurveysiin painamalla "
                 "\"k\": ").lower() == "k"


def create_new_survey(credentials):
    import create_new_survey
    return create_new_survey.create_survey(company_survey_json_data,
                                           credentials=credentials)


def update_survey_data_and_save(new_survey_json_data):
    # Update id into survey.
    company_survey_json_data["id"] = new_survey_json_data["id"]
    with open("./{0}/{1}/{2}/survey.json".format(SURVEY_DATA_BASE_PATH,
                                                 company_name,
                                                 survey_name), "w") as outfile:
        json.dump(company_survey_json_data, outfile, indent=2,
                  ensure_ascii=False)


def rename_survey(survey_id, name, survey_status, credentials):
    headers = {"Content-Type": "application/json"}
    url = "https://fluidsurveys.com/api/v3/surveys/{}/".format(
        survey_id)
    data = json.dumps({"name": name, "live": survey_status})

    # TODO: use edit_survey
    ren = requests.put(url,
                       auth=(credentials["email"], credentials["password"]),
                       headers=headers, data=data)
    if ren.status_code == 200:
        company_survey_json_data["name"] = ren.json()["name"]
        with open("./{0}/{1}/{2}/survey.json".format(SURVEY_DATA_BASE_PATH,
                                                     company_name,
                                                     survey_name),
                  "w") as outfile:
            json.dump(company_survey_json_data, outfile, indent=2,
                      ensure_ascii=False)
    # TODO: Add error handling.


print("Tervetuloa luomaan IMQ-kyselyä!")
survey_info = get_company_name_and_survey_name()
company_name = survey_info["company_name"]
survey_name = survey_info["survey_name"]
overlay_survey_json_data = get_overlay_survey(company_name, survey_name)
if not overlay_survey_json_data:
    print("Sinun täytyy luoda kyselykohtainen overlay.json-tiedosto.")
    exit()
print("Haetaan olemassa olevat kyselyt.")
credentials = get_credentials()
surveys = get_existing_surveys(credentials)
if is_existing_survey(company_name, survey_name, surveys):
    print("Kysely on jo olemassa. Poista vanha kysely FluidSurveysista")
    # TODO: Add possibility to delete existing survey.
    exit()
else:
    print("Kyselyä ei löytynyt. Luodaan uusi kysely.")
questions_version = get_latest_questions_version()
print("Käytetään IMQ-kysymyspatteriston versiota {}".format(questions_version))
company_survey_json_data = get_flattened_questions()

# Update main attributes.
company_survey_json_data["name"] = overlay_survey_json_data["name"]
company_survey_json_data["title"] = overlay_survey_json_data["name"]
company_survey_json_data["IMQ_VERSION"] = company_survey_json_data["version"]
if not overlay_survey_json_data["live"]:
    company_survey_json_data["live"] = 0
else:
    company_survey_json_data["live"] = overlay_survey_json_data["live"]

del company_survey_json_data["version"]

number_of_default_questions = len(company_survey_json_data["form"][0][
                                  "children"])
print("\nLisättiin {0} peruskysymystä".format(number_of_default_questions))

print("\nTarkistetaan yrityskohtaiset tiedot virheiden varalta")
overlay_questions_status = validate_overlay_question_ids()
if overlay_questions_status["error"] == True:
    print("Tapahtui virhe: {0}".format(overlay_questions_status["message"]))
    exit()
else:
    print("Virheitä ei löytynyt.")
print("Lisätään yrityskohtaiset tiedot.")
merge_overlay_questions()

number_of_questions = len(company_survey_json_data["form"][0]["children"])
print("Kysymysten lisääminen on valmis. Kysely sisältää {0} kysymystä.\n"
      .format(number_of_questions))

paginate_survey()
company_frame_json_data = get_survey_frame()
get_overlay_frame_and_merge_with_master()
add_survey_frame()

# Uncomment for debugging.
# print(json.dumps(company_frame_json_data, indent=4, ensure_ascii=False))

with open("./{0}/{1}/{2}/survey.json".format(SURVEY_DATA_BASE_PATH,
                                             company_name,
                                             survey_name), "w") as outfile:
    json.dump(company_survey_json_data, outfile, indent=2, ensure_ascii=False)

if query_create_new_survey():
    print("Lisätään kysely")
    new_survey_json_data = create_new_survey(credentials)
    if not new_survey_json_data:
        print("Jotain tapahtui")
    else:
        update_survey_data_and_save(new_survey_json_data)
        print("Päivitetään kyselyn nimi.")
        rename_survey(company_survey_json_data["id"],
                      "{0}-{1}".format(company_name, survey_name),
                      company_survey_json_data["live"], credentials)
        print("Kysely on nyt luotu.")
else:
    print("Loppu")
