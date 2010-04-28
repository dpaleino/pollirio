while true; do inotifywait tests.py; clear; nosetests tests.py; done
