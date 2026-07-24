"""Versioned, data-oriented catalog package consumed by Aegis.

This package derives a machine-readable role catalog and provenance manifest from
``scaffold/roster.py`` (the single source of truth). It grants no runtime authority:
model, tool, skill, and handoff fields are advisory metadata only.
"""

PACKAGE_VERSION = "1.0.0-aegis.0"
CATALOG_SCHEMA_VERSION = "1"
