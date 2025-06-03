#! /bin/sh
celery -A core worker -l info -Q main-queue -B