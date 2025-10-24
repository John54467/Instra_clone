"""Minimal migration placeholder to satisfy dependency from comments.0001_initial.

This project previously referenced a migration named 0002_tag_post_tags but the
source file is missing (only compiled .pyc files existed). Creating an empty
placeholder migration allows Django to continue applying later app migrations.

If the original 0002 migration contained model/schema changes that are not
present in the DB, this placeholder will not recreate them. In that case you
should restore the original migration or recreate the schema changes properly.
"""
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("clone", "0001_initial"),
    ]

    operations = [
        # Intentionally empty placeholder migration
    ]
