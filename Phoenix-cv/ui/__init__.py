"""
Module UI Phoenix CV
Interface utilisateur securisee modulaire
"""

from .home_page import render_home_page_secure
from .create_cv_page import render_create_cv_page_secure
from .upload_cv_page import render_upload_cv_page_secure
from .templates_page import render_templates_page_secure
from .pricing_page import render_pricing_page_secure
from .common_components import render_secure_header, render_secure_footer
from .display_components import (
    display_generated_cv_secure,
    display_parsed_cv_secure,
    display_ats_results_secure,
    create_demo_profile_secure
)

__all__ = [
    'render_home_page_secure',
    'render_create_cv_page_secure', 
    'render_upload_cv_page_secure',
    'render_templates_page_secure',
    'render_pricing_page_secure',
    'render_secure_header',
    'render_secure_footer',
    'display_generated_cv_secure',
    'display_parsed_cv_secure',
    'display_ats_results_secure',
    'create_demo_profile_secure'
]