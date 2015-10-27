@ECHO off
cd /d "%HOMEDRIVE%%HOMEPATH%/Dropbox/Filosofian akatemia - IMQ/"
:: Uncomment for debugging.
:: py "%HOMEDRIVE%%HOMEPATH%/devel/imq/generate_company_survey.py"
py skriptit/generate_company_survey.py %*
PAUSE
