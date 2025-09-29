# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import sphinx_bootstrap_theme 
sys.path.insert(1, '..')

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Michael J. Pye'
copyright = '2025, Michael John Pye'
author = 'Michael Pye'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['myst_nb', 'sphinx_new_tab_link']

#new_tab_link_show_external_link_icon = True    #adds icon to tell the user that the link they are about to click on will open in a new tab

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'bootstrap'
html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()
html_static_path = ['_static']
html_css_files = ['custom.css']
html_logo = '_static/headshot.jpg'
html_favicon = '_static/headshot.jpg'
html_title = "Michael J. Pye"

# Theme options are theme-specific and customize the look and feel of a
# theme further.
html_theme_options = {
    # Navigation bar title. (Default: ``project`` value)
    'navbar_title': 'Michael J. Pye',

    # Tab name for entire site. (Default: 'Site')
    'navbar_site_name': 'Michael J. Pye',

    # A list of tuples containing pages or urls to link to.
    # Valid tuples should be in the following forms:
    #    (name, page)                 # a link to a page
    #    (name, '/aa/bb', 1)          # a link to an arbitrary relative url
    #    (name, 'http://example.com', True) # arbitrary absolute url
    # Note the "1" or "True" value above as the third argument to indicate
    # an arbitrary url.
    'navbar_links': [
        ('Experience', 'experience'),
        ('Projects', 'projects'),
        ('Publications', 'publications'),
        ('About Me', 'about_me'),
        ('Contact', 'contact'),
    ],

    # Render the next and previous page links in navbar. (Default: true)
    'navbar_sidebarrel': False,

    # Render the current pages TOC in the navbar. (Default: true)
    'navbar_pagenav': False,

    # Tab name for the current pages TOC. (Default: 'Page')
    'navbar_pagenav_name': 'Page',

    # Global TOC depth for "site" navbar tab. (Default: 1)
    # Switching to -1 shows all levels.
    'globaltoc_depth': 1,

    # Include hidden TOCs in Site navbar?
    #
    # Note: If this is "false", you cannot have mixed ``:hidden:`` and
    # non-hidden ``toctree`` directives in the same page, or else the build
    # will break.
    #
    # Values: "true" (default) or "false"
    'globaltoc_includehidden': 'false',

    # HTML navbar class (Default: 'navbar') to attach to <div> element.
    # For black navbar, do "navbar navbar-inverse"
    'navbar_class': 'navbar navbar-inverse',

    # Fix navigation bar to top of page?
    # Values: "true" (default) or "false"
    'navbar_fixed_top': 'true',

    # Location of link to source.
    # Options are "nav" (default), "footer" or anything else to exclude.
    'source_link_position': 'footer',

    # Bootswatch (http://bootswatch.com/) theme.
    #
    # Options are nothing (default) or the name of a valid theme
    # such as "cosmo" or "sandstone".
    #
    # The set of valid themes depend on the version of Bootstrap
    # that's used (the next config option).
    #
    # Currently, the supported themes are:
    # - Bootstrap 2: https://bootswatch.com/2
    # - Bootstrap 3: https://bootswatch.com/3
    'bootswatch_theme': 'united',

    # Choose Bootstrap version.
    # Values: "3" (default) or "2" (in quotes)
    'bootstrap_version': '3',
}

#modify the sidebar to remove the search box, "previous" and "next" links, and "view page source" link
html_sidebars = {
    # apply to all pages:
    "**": [
        "localtoc.html",     # per-page TOC (or use 'globaltoc.html' if you prefer)
        # <-- note: NO 'sourcelink.html' here
        # <-- note: NO 'searchbox.html' here
        # <-- note: NO 'relations.html' here
    ],
}