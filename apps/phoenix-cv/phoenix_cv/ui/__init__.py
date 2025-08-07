"""
Module UI Phoenix CV
Interface utilisateur securisee modulaire
"""

from phoenix_cv.ui.common_components import render_secure_footer, render_secure_header
from phoenix_cv.ui.create_cv_page import render_create_cv_page_secure
from phoenix_cv.ui.display_components import (
    create_demo_profile_secure,
    display_ats_results_secure,
    display_generated_cv_secure,
    display_parsed_cv_secure,
)
from phoenix_cv.ui.home_page import render_home_page_secure
from phoenix_cv.ui.pricing_page import render_pricing_page_secure
from phoenix_cv.ui.templates_page import render_templates_page_secure
from phoenix_cv.ui.upload_cv_page import render_upload_cv_page_secure

__all__ = [
    "render_home_page_secure",
    "render_create_cv_page_secure",
    "render_upload_cv_page_secure",
    "render_templates_page_secure",
    "render_pricing_page_secure",
    "render_secure_header",
    "render_secure_footer",
    "display_generated_cv_secure",
    "display_parsed_cv_secure",
    "display_ats_results_secure",
    "create_demo_profile_secure",
]
