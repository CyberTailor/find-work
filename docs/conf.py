# SPDX-FileCopyrightText: 2022-2024 Anna <cyber@sysrq.in>
# SPDX-License-Identifier: CC0-1.0
#
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'find-work'
author = 'Anna (cybertailor) Vyalkova'
copyright = f'2024, {author}'
release = '0.3.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx_prompt',
]

try:
    import notfound.extension
    extensions.append('notfound.extension')

    notfound_urls_prefix = None
except ModuleNotFoundError:
    pass

try:
    import sphinx_sitemap
    extensions.append('sphinx_sitemap')

    sitemap_locales = [None]
    sitemap_url_scheme = '{link}'
except ModuleNotFoundError:
    pass

root_doc = 'toc'
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
manpages_url = 'https://docs.sysrq.in/{path}'

extlinks = {
    'bug': ('https://bugs.sysrq.in/show_bug.cgi?id=%s', 'bug #%s'),
    'pypi': ('https://pypi.org/project/%s/', '%s'),
}
intersphinx_mapping = {
    'aiohttp': ('https://docs.aiohttp.org/en/stable', None),
    'click': ('https://click.palletsprojects.com/en/latest', None),
    'requests': ('https://requests.readthedocs.io/en/latest/', None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'insipid'
html_permalinks_icon = '#'
html_theme_options = {
    'globaltoc_maxdepth': 3,
    'right_buttons': ['git-button.html'],
}
html_sidebars = {
    '**': [
        'globaltoc.html',
    ]
}
html_context = {
    'git_repo_url': 'https://git.sysrq.in/find-work/about/',
}

html_static_path = ['_static']
html_title = f'{project} {release}'
html_baseurl = 'https://find-work.sysrq.in/'
