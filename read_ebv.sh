#!/bin/bash

# Read and print all variables from .env file
while IFS= read -r line; do
    # Skip empty lines and comments
    [[ -z "$line" || "$line" =~ ^# ]] && continue
    echo "$line"
done < .env