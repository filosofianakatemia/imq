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

single_choice_grid_description = {
    "description": {
        "fi": "1: Ei lainkaan, 2: Huonosti, " +
              "3: Melko huonosti, 4: Jossain määrin, 5: Melko hyvin, " +
              "6: Hyvin, 7: Erittäin hyvin",
        "en": "1: Not at all, 2: Poorly, " +
              "3: Somewhat poorly, 4: To some extent, 5: Pretty well, " +
              "6: Well, 7: Very well"
    },
    "idname": "section-separator",
    "title": {
        "fi": "Arvioi, miten hyvin seuraavat väitteet pitävät paikkansa työssäsi.",
        "en": "Rate how well the following statements are reflected in your job."
    },
    "type": "question"
}

def read_json_file(json_file_path):
    with open(json_file_path, encoding="utf8") as json_file:
        # TODO: check that file has content.
        return json.load(json_file)


def remove_question(question_id):
    for entry in company_survey_json_data["form"]:
        if "children" in entry:
            # http://stackoverflow.com/a/16143537
            # http://stackoverflow.com/a/9755790
            for child_entry in entry["children"]:
                if child_entry["id"] == question_id:
                    child_entry_title = child_entry["title"]["fi"] if "fi" in child_entry["title"] else child_entry["title"]["en"]
                    print("poista\t{0}\t\"{1}\"".
                          format(child_entry["id"],
                                 child_entry_title))
                    entry["children"].remove(child_entry)
                    break

    # Remove references from sum formulas.
    remove_question_from_sum_formulas(question_id)
    print("")


def remove_question_from_sum_formulas(variable_id):
    if "SPSS_SUM_FORMULAS" in company_survey_json_data:
        for formula_entry in company_survey_json_data["SPSS_SUM_FORMULAS"]:
            if variable_id in formula_entry["children"]:
                print(("Poista kysymys {0} kaavasta {1}")
                      .format(variable_id, formula_entry["id"]))
                # Remove variable from sum formula.
                formula_entry["children"].remove(variable_id)


def insert_question_before(id, question):
    for entry in company_survey_json_data["form"]:
        if "children" in entry:
            for index, child_entry in enumerate(entry["children"]):
                if child_entry["id"] == id:
                    question_title = question["title"]["fi"] if "fi" in question["title"] else question["title"]["en"]
                    child_entry_title = child_entry["title"]["fi"] if "fi" in child_entry["title"] else child_entry["title"]["en"]
                    print("lisää\t{0}\t\"{1}\"\n"
                          "ennen\t{2}\t\"{3}\"\n"
                          "indeksi\t{4}\n".
                          format(question["id"], question_title,
                                 child_entry["id"], child_entry_title,
                                 index))
                    entry["children"].insert(index, question)
                    break


def insert_question_after(id, question):
    for entry in company_survey_json_data["form"]:
        if "children" in entry:
            for index, child_entry in enumerate(entry["children"]):
                if child_entry["id"] == id:
                    question_title = question["title"]["fi"] if "fi" in question["title"] else question["title"]["en"]
                    child_entry_title = child_entry["title"]["fi"] if "fi" in child_entry["title"] else child_entry["title"]["en"]
                    print("lisää\t{0}\t\"{1}\"\n"
                          "jälkeen\t{2}\t\"{3}\"\n"
                          "indeksi\t{4}\n".
                          format(question["id"], question_title,
                                 child_entry["id"], child_entry_title,
                                 index + 1))
                    entry["children"].insert(index + 1, question)
                    break


def rename_question(id, question):
    for entry in company_survey_json_data["form"]:
        if "children" in entry:
            for index, child_entry in enumerate(entry["children"]):
                if child_entry["id"] == id:
                    question_title = question["title"]["fi"] if "fi" in question["title"] else question["title"]["en"]
                    child_entry_title = child_entry["title"]["fi"] if "fi" in child_entry["title"] else child_entry["title"]["en"]
                    print("nimettiin\t{0}\t\"{1}\"\n"
                          "uudelleen\t\t\"{2}\""
                          .format(child_entry["id"],
                                  child_entry_title,
                                  question_title))
                    child_entry["title"] = question["title"]
                    if "description" in question:
                        child_entry["description"] = question["description"]
                    break


def insert_frame_question_after(id, question):
    for entry in company_frame_json_data:
        if "children" in entry:
            for index, child_entry in enumerate(entry["children"]):
                if child_entry["id"] == id:
                    question_title = question["title"]["fi"] if "fi" in question["title"] else question["title"]["en"]
                    child_entry_title = child_entry["title"]["fi"] if "fi" in child_entry["title"] else child_entry["title"]["en"]
                    print("lisää\t{0}\t\"{1}\"\n"
                          "jälkeen\t{2}\t\"{3}\"\n"
                          "indeksi\t{4}\n".
                          format(question["id"], question_title,
                                 child_entry["id"], child_entry_title,
                                 index + 1))
                    entry["children"].insert(index + 1, question)
                    break


def remove_frame_question(question_id):
    for entry in company_frame_json_data:
        if "children" in entry:
            for index, child_entry in enumerate(entry["children"]):
                if child_entry["id"] == question_id:
                    child_entry_title = child_entry["title"]["fi"] if "fi" in child_entry["title"] else child_entry["title"]["en"]
                    print(("poista\t{0}\t\"{1}\"\n")
                          .format(child_entry["id"],
                                  child_entry_title))
                    entry["children"].remove(child_entry)

def remove_frame_empty_pages():
    for entry in company_frame_json_data:
        if not "children" in entry or not entry["children"]:
            print("poistetaan tyhjä sivu")
            company_frame_json_data.remove(entry)


def rename_frame_question(question_id, question):
    for entry in company_frame_json_data:
        if "children" in entry:
            for index, child_entry in enumerate(entry["children"]):
                if child_entry["id"] == question_id:
                    question_title = question["title"]["fi"] if "fi" in question["title"] else question["title"]["en"]
                    child_entry_title = child_entry["title"]["fi"] if "fi" in child_entry["title"] else child_entry["title"]["en"]
                    if "title" in question:
                        print("nimettiin\t{0}\t\"{1}\"\n"
                              "uudelleen\t\t\"{2}\""
                              .format(child_entry["id"],
                                      child_entry_title,
                                      question_title))
                        child_entry["title"] = question["title"]
                    if "description" in question:
                        print("nimettiin kysymyksen\t{0}\t\"{1}\"\n"
                              "sisältö uudelleen"
                              .format(child_entry["id"],
                                      child_entry_title))
                        child_entry["description"] = question["description"]
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
                    else:
                        if not has_affect_question(default_question_ids,
                                                   question[affect_id_type]):
                            message = ("Kysymyksen {0} kentän {1} arvo {2} ei "
                                       "viittaa mihinkään olemassa olevaan "
                                       "tai lisättävään kysymykseen").format(
                                question["id"], affect_id_type,
                                question[affect_id_type])
                            invalid_overlay = True
                        if (affect_id_type != "DELETE_ID" and
                                affect_id_type != "RENAME_ID"):
                            if question[affect_id_type] == question["id"]:
                                message = ("Kysymyksen id {0} on sama kuin "
                                           "kysymyksen kenttä {1}"
                                           .format(question["id"],
                                                   affect_id_type))
                                invalid_overlay = True
                                break
                            elif is_question_to_be_removed(question[
                                                           affect_id_type]):
                                message = ("Kysymys {0} viittaa poistettavaan "
                                           "kysymykseen {1}"
                                           .format(question["id"],
                                                   question[affect_id_type]))
                                invalid_overlay = True
                            elif duplicate_reference(question["id"],
                                                     question[affect_id_type],
                                                     affect_id_type):
                                message = ("Kysymykseen {0} useampi kuin yksi "
                                           "viittaus tyyppiä {1}").format(
                                    question[affect_id_type],
                                    affect_id_type)
                                invalid_overlay = True
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


def has_affect_question(default_question_ids, affect_id):
    has_affect_question = affect_id in default_question_ids
    if not has_affect_question and "form" in overlay_survey_json_data:
        for i in overlay_survey_json_data["form"]:
            if "children" in i:
                for question in i["children"]:
                    if "id" in question and question["id"] == affect_id:
                        has_affect_question = True
                        break
    return has_affect_question


def duplicate_reference(question_id, affect_id, affect_id_type):
    if "form" in overlay_survey_json_data:
        for i in overlay_survey_json_data["form"]:
            if "children" in i:
                for question in i["children"]:
                    if ("id" in question and question["id"] != question_id and
                        affect_id_type in question and
                            question[affect_id_type] == affect_id):
                        return True


def is_question_to_be_removed(question_id):
    if "form" in overlay_survey_json_data:
        for i in overlay_survey_json_data["form"]:
            if "children" in i:
                for question in i["children"]:
                    if ("DELETE_ID" in question and
                            question["DELETE_ID"] == question_id):
                        return True


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
    QUESTIONS_IN_PAGE = 11
    for index, entry in enumerate(company_survey_json_data["form"]):

        single_choice_grid_description_copy = copy.deepcopy(
            single_choice_grid_description)
        single_choice_grid_description_copy["id"] = str(uuid.uuid1())
        company_survey_json_data["form"][index]["children"].insert(
            0, single_choice_grid_description_copy)

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
            if "type" in entry and entry["type"] == "page" and "INSERT_TO" in entry:
                if entry["INSERT_TO"] == "START":
                    company_frame_json_data.insert(0, entry)
                elif entry["INSERT_TO"] == "END":
                    company_frame_json_data.append(entry)
            elif "children" in entry:
                for child_entry in entry["children"]:
                    if "DELETE_ID" in child_entry:
                        remove_frame_question(child_entry["DELETE_ID"])
                    elif "BEFORE_ID" in child_entry:
                        print("before")
                    elif "AFTER_ID" in child_entry:
                        insert_frame_question_after(child_entry["AFTER_ID"],
                                                    child_entry)
                    elif "RENAME_ID" in child_entry:
                        rename_frame_question(child_entry["RENAME_ID"],
                                              child_entry)
        # If the page does not have any children anymore, remove entire page
        remove_frame_empty_pages()

def add_survey_frame():
    # Add survey frame. Last question goes to the end of the survey.
    PREPENDING_QUESTIONS_IN_FRAME = len(company_frame_json_data) - 1
    company_survey_json_data["form"] = company_frame_json_data[
        :PREPENDING_QUESTIONS_IN_FRAME] + company_survey_json_data[
        "form"] + company_frame_json_data[PREPENDING_QUESTIONS_IN_FRAME:]


def merge_sum_formulas():
    if "SPSS_SUM_FORMULAS" in overlay_survey_json_data:
        for overlay_entry in overlay_survey_json_data["SPSS_SUM_FORMULAS"]:
            existing_entry = False
            for sum_entry in company_survey_json_data["SPSS_SUM_FORMULAS"]:
                if overlay_entry["id"] == sum_entry["id"]:
                    # append
                    existing_entry = True
                    # http://stackoverflow.com/a/3749835
                    sum_entry["children"] = list(
                        set(overlay_entry["children"] + sum_entry["children"]))
                    sum_entry["formulas"] = list(
                        set(overlay_entry["formulas"] + sum_entry["formulas"]))
                    break
            if not existing_entry:
                # add new
                company_survey_json_data[
                    "SPSS_SUM_FORMULAS"].append(overlay_entry)


def remove_orphan_sum_formulas():
    removed_formula_id = None
    for formula_entry in company_survey_json_data["SPSS_SUM_FORMULAS"]:
        remove_sum_formulas_without_references(
            formula_entry["children"], formula_entry["id"])
        if not formula_entry["children"]:
            # NOTE: Question could - theoretically - be the only
            #       (remaining) child in the sum formula.
            #       In that case the formula is to be removed as well -
            #       and recursively check is the formula id used in
            #       remaining sum formulas.
            company_survey_json_data[
                "SPSS_SUM_FORMULAS"].remove(formula_entry)
            removed_formula_id = formula_entry["id"]
            break

    if removed_formula_id:
        print("Poista summamuuttuja {} kaavoista".format(removed_formula_id))
        remove_formula_order(removed_formula_id)
        # Recursively remove variable(s) from formulas
        remove_variable_from_sum_formulas(removed_formula_id)
        remove_orphan_sum_formulas()


def remove_variable_from_sum_formulas(variable_id):
    removed_formula_id = None
    for formula_entry in company_survey_json_data["SPSS_SUM_FORMULAS"]:
        if variable_id in formula_entry["children"]:
            # Remove variable from sum formula.
            print(("Poista muuttuja {0} kaavasta {1}")
                  .format(variable_id, formula_entry["id"]))
            formula_entry["children"].remove(variable_id)
            if not formula_entry["children"]:
                removed_formula_id = formula_entry["id"]
                break

    if removed_formula_id:
        print("Poista {} kaavoista".format(
              removed_formula_id))
        # Recursively remove variable(s) from formulas
        remove_orphan_sum_formulas()


def remove_sum_formulas_without_references(sum_formula_references,
                                           formula_name):
    variables_to_remove = []
    for reference in sum_formula_references:
        is_reference = False
        for entry in company_survey_json_data["form"]:
            if reference_is_question(entry["children"], reference):
                is_reference = True
                break
            if reference_is_sum_id(reference):
                is_reference = True
                break
            if has_reference(entry, reference):
                is_reference = True
                break

        if not is_reference and reference not in variables_to_remove:
            variables_to_remove.append(reference)

    if variables_to_remove:
        for variable_to_remove in variables_to_remove:
            print(("Poista summamuuttuja {0} kaavasta {1}")
                  .format(variable_to_remove, formula_name))
            sum_formula_references.remove(variable_to_remove)
            remove_formula_order(variable_to_remove)


def remove_formula_order(formula_id):
    if "SPSS_FORMULAS_ORDER" in company_survey_json_data:
        # http://stackoverflow.com/a/1207427
        for formula in company_survey_json_data["SPSS_FORMULAS_ORDER"][:]:
            if formula["id"] == formula_id:
                company_survey_json_data["SPSS_FORMULAS_ORDER"].remove(formula)


def has_reference(entry, reference):
    if "children" in entry:
        for child_entry in entry["children"]:
            if "SPSS_FORMULAS" in child_entry:
                for formula_reference in child_entry["SPSS_FORMULAS"]:
                    if (formula_reference["name"] == "average" and
                            reference in formula_reference["ids"]):
                        # Found what we needed, end the loop.
                        # Only the variables generated from average formula ids
                        # may be used in the sum forumulas.
                        return True
    return False


def reference_is_sum_id(reference):
    for formula_entry in company_survey_json_data["SPSS_SUM_FORMULAS"]:
        if reference == formula_entry["id"]:
            return True
    return False


def reference_is_question(survey_entries, reference):
    for child_entry in survey_entries:
        if child_entry["id"] == reference:
            return True
    return False


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
if len(sys.argv) != 6 or sys.argv[5] != "BYPASS":
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
if "languages" in overlay_survey_json_data:
    company_survey_json_data["languages"] = overlay_survey_json_data["languages"]
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
print("Lisätään analyysisyntaksin tiedot.")
merge_sum_formulas()
print("Analyysisyntaksin tiedot lisätty. Poistetaan syntaksin muuttujat, "
      "joihin ei ole viitteitä")
remove_orphan_sum_formulas()
print("")

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
