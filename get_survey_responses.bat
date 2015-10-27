@ECHO off
cd /d "%HOMEDRIVE%%HOMEPATH%/Dropbox/Filosofian akatemia - IMQ/"
:: Uncomment for debugging.
:: "%HOMEDRIVE%%HOMEPATH%/devel/imq/get_survey_responses.py"
py skriptit/get_survey_responses.py
PAUSE
