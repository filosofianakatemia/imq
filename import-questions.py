import copy
import json
import math
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
            "required": True,
            "type": "string"
        }
    ]
}

master_json_data = {
    "title": "IMQ Kysymyspatteristo 1.4",
    "version": 1.4,
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
    "title": "IMQ Kysymyspatteristo 1.4",
    "version": 1.4,
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
    line.rstrip('\n') for line in open("./reverse_question_ids_1.4.txt")]

with open("./questions_1.4.txt") as questions_file:
    for index, line in enumerate(questions_file):
        question_id = line[:12].strip()
        title = line[12:].strip()

        if question_id == "avoin":
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

# Uncomment for debugging.
# print(json.dumps(master_json_data["form"][0]["children"],
#                  indent=4, sort_keys=True))

# Add survey frame
with open("./master_frame.json") as master_frame_json_file:
    master_frame_json_data = json.load(master_frame_json_file)
    PREPENDING_QUESTIONS_IN_FRAME = len(master_frame_json_data) - 1
    master_json_data["form"] = master_frame_json_data[
        :PREPENDING_QUESTIONS_IN_FRAME] + master_json_data[
        "form"] + master_frame_json_data[PREPENDING_QUESTIONS_IN_FRAME:]

with open("./master_latest.json", "w") as outfile:
    json.dump(master_json_data, outfile, indent=2, ensure_ascii=False)

with open("./master_latest_flattened.json", "w") as outfile:
    json.dump(master_json_data_flattened, outfile, indent=2,
              ensure_ascii=False)
