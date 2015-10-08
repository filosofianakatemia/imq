#!/bin/sh

rsync -a --delete --exclude 'pre-push.sh' --exclude '*.sublime-project' --exclude '*.sublime-workspace' --delete-excluded ~/devel/imq/ ~/Dropbox/Filosofian\ Akatemia\ -\ IMQ/skriptit
