# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import sphinx_bootsrap_theme
sys.path.insert(1, '..')

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Michael John Pye\'s Portfolio'
copyright = '2025, Michael John Pye'
author = 'Michael Pye'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['myst_nb', 'sphinx_new_tab_link']

new_tab_link_show_external_link_icon = True    #adds icon to tell the user that the link they are about to click on will open in a new tab

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx-bootstrap-theme'
html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()
html_static_path = ['_static']
html_logo = 'sphinx/_static/headshot.jpg'
