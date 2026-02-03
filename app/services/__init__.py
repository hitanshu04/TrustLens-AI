"""
Service layer for the Scam Detection API.

This package contains the risk scoring engine and supporting utilities
such as URL reputation checks. The design is intentionally modular so
that additional detectors (e.g. ML models) can be added without
changing the API surface.
"""
