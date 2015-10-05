import getpass
import os.path

SURVEY_DATA_BASE_PATH = "data"


def query_company_name_and_survey_name():
    survey_info = {}

    # http://stackoverflow.com/a/18413162
    while True:
        survey_info["company_name"] = input("Yrityksen nimi: ")
        survey_info["survey_name"] = input("Kyselyn nimi: ")
        if (survey_info["company_name"] and survey_info["survey_name"] and
                os.path.isdir("{0}/{1}/{2}"
                              .format(SURVEY_DATA_BASE_PATH,
                                      survey_info["company_name"],
                                      survey_info["survey_name"]))):
            break
        else:
            print("Kyselyä antamillasi tiedoilla ei löydy. Tarkista "
                  "yrityksen ja kyselyn nimi ja että olet luonut "
                  "hakemistot.")

    return survey_info


def query_credentials():
    email = input("Sähköposti: ")
    password = getpass.getpass()
    return {"email": email, "password": password}
