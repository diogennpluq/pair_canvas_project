#!/bin/bash

# Generate a secure SECRET_KEY for Django
# Usage: ./generate_secret_key.sh

python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
