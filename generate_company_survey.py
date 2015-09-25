import copy
import getpass
import json
import os.path
import requests
import sys
import uuid
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
                                 child_entry["title"]))
                    entry["children"].remove(child_entry)
                    break


def insert_question_after(id, question):
    for entry in company_survey_json_data["form"]:
        if "children" in entry:
            for index, child_entry in enumerate(entry["children"]):
                if child_entry["id"] == id:
                    print("lisää\t{0}\t\"{1}\"\n"
                          "jälkeen\t{2}\t\"{3}\"\n"
                          "indeksi\t{4}\n".
                          format(question["id"], question["title"],
                                 child_entry["id"], child_entry["title"],
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


def insert_question_before(id, question):
    for entry in company_survey_json_data["form"]:
        if "children" in entry:
            for index, child_entry in enumerate(entry["children"]):
                if child_entry["id"] == id:
                    print("lisää\t{0}\t\"{1}\"\n"
                          "ennen\t{2}\t\"{3}\"\n"
                          "indeksi\t{4}\n".
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
                    print("lisää\t{0}\t\"{1}\"\n"
                          "jälkeen\t{2}\t\"{3}\"\n"
                          "indeksi\t{4}\n".
                          format(question["id"], question["title"],
                                 child_entry["id"], child_entry["title"],
                                 index + 1))
                    entry["children"].insert(index + 1, question)
                    break


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


def get_company_and_survey_name():
    global company_name
    global survey_name

    # http://stackoverflow.com/a/18413162
    if len(sys.argv) < 2:
        while True:
            company_name = input("Yrityksen nimi: ")
            survey_name = input("Kyselyn nimi: ")
            if (company_name and survey_name and
                    os.path.isdir("{0}/{1}/{2}".format(SURVEY_DATA_BASE_PATH,
                                                       company_name,
                                                       survey_name))):
                break
            else:
                print("Kyselyä antamillasi tiedoilla ei löydy. Tarkista "
                      "yrityksen ja kyselyn nimi ja että olet luonut "
                      "hakemistot.")
    else:
        company_name = sys.argv[1]
        survey_name = sys.argv[2]


def get_overlay_survey(company_name, survey_name):
    overlay_survey_json_file_path = "./{0}/{1}/{2}/overlay.json".format(
        SURVEY_DATA_BASE_PATH, company_name, survey_name)
    if os.path.isfile(overlay_survey_json_file_path):
        overlay_survey_json_data = (read_json_file(
                                    overlay_survey_json_file_path))
        return overlay_survey_json_data


def query_credentials():
    if len(sys.argv) < 4:
        email = input("Sähköposti: ")
        password = getpass.getpass()
    else:
        email = sys.argv[3]
        password = sys.argv[4]

    return {"email": email, "password": password}


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


def rename_survey(survey_id, name, credentials):
    headers = {"Content-Type": "application/json"}
    url = "https://fluidsurveys.com/api/v3/surveys/{}/".format(
        survey_id)
    data = json.dumps({"name": name})

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
company_name = None
survey_name = None
get_company_and_survey_name()
overlay_survey_json_data = get_overlay_survey(company_name, survey_name)
if not overlay_survey_json_data:
    print("Sinun täytyy luoda kyselykohtainen overlay.json-tiedosto.")
    exit()
print("Haetaan olemassa olevat kyselyt.")
credentials = query_credentials()
surveys = get_existing_surveys(credentials)
if is_existing_survey(company_name, survey_name, surveys):
    print("Kysely on jo olemassa. Poista vanha kysely FluidSurveysista")
    # TODO: Add possibility to delete existing survey.
    exit()
else:
    print("Kyselyä ei löytynyt. Luodaan uusi kysely.")
questions_version = get_latest_questions_version()
company_survey_json_data = get_flattened_questions()

# Update main attributes.
company_survey_json_data["name"] = overlay_survey_json_data["name"]
company_survey_json_data["title"] = overlay_survey_json_data["name"]
company_survey_json_data["IMQ_VERSION"] = company_survey_json_data["version"]
del company_survey_json_data["version"]

number_of_default_questions = len(company_survey_json_data["form"][0][
                                  "children"])
print("\nLisättiin {0} peruskysymystä".format(number_of_default_questions))

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
                      credentials)
        print("Kysely on nyt luotu.")
else:
    print("Loppu")
