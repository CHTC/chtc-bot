#!/usr/bin/env bash

set -e

# temporary fix until we actually have a migration
mkdir -p /app/migrations/versions
flask db upgrade
