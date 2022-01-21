# -- Project information

project = "Bayesian Workflow resources"
author = "ArviZ contributors"
copyright = f"2022, {author}"

version = "0.1.0"
release = version


# -- General configuration

extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "myst_nb",
    "sphinx_copybutton",
    "sphinx_design",
]

templates_path = ["sphinx/_templates"]

exclude_patterns = [
    "Thumbs.db",
    ".DS_Store",
    ".ipynb_checkpoints",
    "**/*.md",
    "**/*jl.ipynb",
    "README.md",
    "jupyter_execute",
    "_build",
]

# The reST default role (used for this markup: `text`) to use for all documents.
default_role = "code"

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = False

# -- Options for extensions

jupyter_execute_notebooks = "auto"
execution_excludepatterns = ["*.ipynb"]
myst_enable_extensions = ["colon_fence", "deflist", "dollarmath", "amsmath"]

# -- Options for HTML output

html_theme = "sphinx_book_theme"
# html_static_path = ["sphinx/_static"]
# html_css_files = ["custom.css"]
html_theme_options = {
    "repository_url": "https://github.com/arviz-devs/bayesian-workflow",
    "repository_branch": "main",
    "use_repository_button": True,
    "use_issues_button": True,
    "use_edit_page_button": True,
    "use_download_button": True,
}

intersphinx_mapping = {
    "arviz": ("https://arviz-devs.github.io/arviz", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference/", None),
    "xarray": ("http://xarray.pydata.org/en/stable/", None),
}
