#!/bin/bash

.venv/bin/alembic -c /opt/app/alembic.ini upgrade head &
exec .venv/bin/python -m bin
