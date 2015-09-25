import copy
import json
import math
import sys
import uuid

QUESTIONS_BASE_PATH = "kysymykset"

if len(sys.argv) < 2:
    questions_version = input("Enter new version number: ")
else:
    questions_version = sys.argv[1]

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

single_choise_grid = {
    "idname": "single-choice-grid",
    "title": {
        "fi": ""
    },
    "children": [
        {
            "required": True,
            "type": "single"
        }
    ],
    "choices": [
        {
            "label": "1"
        },
        {
            "label": "2"
        },
        {
            "label": "3"
        },
        {
            "label": "4"
        },
        {
            "label": "5"
        },
        {
            "label": "6"
        },
        {
            "label": "7"
        }
    ]
}

text_response = {
    "idname": "text-response",
    "title": {
        "fi": ""
    },
    "children": [
        {
            "required": False,
            "type": "string"
        }
    ]
}

master_json_data = {
    "title": "IMQ Kysymyspatteristo {}".format(questions_version),
    "version": questions_version,
    "form": [],
    "languages": [
        {
            "code": "fi",
            "isDefault": True,
            "name": "Finnish"
        }
    ]
}

master_json_data_flattened = {
    "title": "IMQ Kysymyspatteristo {}".format(questions_version),
    "version": questions_version,
    "form": [{
        "children": [],
        "type": "page"
    }],
    "languages": [
        {
            "code": "fi",
            "isDefault": True,
            "name": "Finnish"
        }
    ]
}

reverse_question_ids = [
    line.rstrip("\n") for line in open("./{0}/{1}/reverse_question_ids_{1}.txt"
                                       .format(QUESTIONS_BASE_PATH,
                                               questions_version))]

with open("./{0}/{1}/questions_{1}.txt"
          .format(QUESTIONS_BASE_PATH, questions_version)) as questions_file:
    for index, line in enumerate(questions_file):
        question_id = line[:12].strip()
        title = line[12:].strip()

        if "avoin" in question_id:
            question = copy.deepcopy(text_response)
        else:
            question = copy.deepcopy(single_choise_grid)
            title += "."  # Add dot to the end of the question.

        question["title"]["fi"] = title
        question["id"] = question_id

        if question_id in reverse_question_ids:
            question["REVERSE_VALUE"] = True

        place = math.floor((index) / 9)

        if len(master_json_data["form"]) <= place:
            question_page_copy = copy.deepcopy(question_page)
            master_json_data["form"].append(question_page_copy)
            single_choise_grid_description_copy = copy.deepcopy(
                single_choise_grid_description)
            single_choise_grid_description_copy["id"] = str(uuid.uuid1())
            master_json_data["form"][place]["children"].append(
                single_choise_grid_description_copy)

        master_json_data["form"][place]["children"].append(question)
        master_json_data_flattened["form"][0]["children"].append(question)

    # http://stackoverflow.com/q/845058
    print("Added {0} questions".format(index + 1))

# Uncomment for debugging.
# print(json.dumps(master_json_data["form"][0]["children"],
#                  indent=4, sort_keys=True))

# Add survey frame
with open("./{0}/{1}/master_frame_{1}.json"
          .format(QUESTIONS_BASE_PATH, questions_version)
          ) as master_frame_json_file:
    master_frame_json_data = json.load(master_frame_json_file)
    # Two last questions go to the end of the survey.
    PREPENDING_QUESTIONS_IN_FRAME = len(master_frame_json_data) - 2
    master_json_data["form"] = master_frame_json_data[
        :PREPENDING_QUESTIONS_IN_FRAME] + master_json_data[
        "form"] + master_frame_json_data[PREPENDING_QUESTIONS_IN_FRAME:]

with open("./{0}/{1}/master_{1}.json"
          .format(QUESTIONS_BASE_PATH, questions_version), "w") as outfile:
    json.dump(master_json_data, outfile, indent=2, ensure_ascii=False)

with open("./{0}/{1}/master_flattened_{1}.json"
          .format(QUESTIONS_BASE_PATH, questions_version), "w") as outfile:
    json.dump(master_json_data_flattened, outfile, indent=2,
              ensure_ascii=False)
