#!/usr/bin/bash

poetry version patch

poetry build

echo "now run \$ poetry publish"
