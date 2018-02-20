sphinxcontrib-cloudformationyaml
================================================================================

This Sphinx autodoc extension documents Cloudformation YAML files from comments and descriptions.

It looks for documentation descriptions and comments delimiter(default: ``# my comment``) and
adds it with all further comments as reST documentation till it finds end of comment.

It does not support Cloudformation JSON files becuase they do not gracefully handle comments.

Options
--------------------------------------------------------------------------------

Options available to use in your configuration:

cloudformationyaml_root
   Look for cloudformation files relatively to this directory.

   **DEFAULT**: ..

cloudformationyaml_comment
   Comment start character(s).

   **DEFAULT**: #

Installing
--------------------------------------------------------------------------------

Issue command:

``pip install sphinxcontrib-cloudformationyaml``

And add extension in your project's ``conf.py``:

.. code-block:: py

   extensions = ["sphinxcontrib.cloudformationyaml"]

Example
--------------------------------------------------------------------------------

.. code-block:: rst

   Some title
   ==========

   Documenting single cloudformation file.

   .. cloudformationyaml:: some_cloudformation_file.yml

   Documenting cloudformation directory.

   .. cloudformationyaml:: some_cloudformation_directory
