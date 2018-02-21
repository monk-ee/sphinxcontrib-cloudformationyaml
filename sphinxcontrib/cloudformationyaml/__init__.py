import os

from docutils.statemachine import ViewList
from docutils.parsers.rst import Directive
from docutils import nodes
import ruamel.yaml
import re
from sphinx.util.nodes import nested_parse_with_titles
from sphinx.ext.autodoc import AutodocReporter


def general_constructor(loader, tag_suffix, node):
    """
    Just a string flattener for custonm yaml tags such as the ones that occur in cfn files

    :param loader: the ruamal.yaml instance
    :param tag_suffix: the tag name
    :param node: the tag node from the loaded yaml file
    :return: t\just the simple node value as a string
    :rtype: string
    """
    return node.value


ruamel.yaml.SafeLoader.add_multi_constructor(u'!', general_constructor)


class CloudformationYAMLException(Exception):
    pass


class CloudformationYAMLDirective(Directive):
    """The main YAML parser"""

    required_arguments = 1
    """Number of required directive arguments."""

    config = None
    """Sphinx environment configuration."""

    env = None
    """Sphinx environment  path."""

    record_dependencies = None
    """Initialize the dependency list, automatically setting the
        output file to `output_file` (see `set_output()`) and adding
        all supplied dependencies."""

    result = None
    """List with extended functionality: slices of ViewList objects are child
    lists, linked to their parents"""

    def run(self):
        """
        The task runner for the rst processing

        :return: list of the document tree element nodes
        :rtype :list: `Docutils document tree element class node`
        :raise CloudformationYAMLException
        """
        self.config = self.state.document.settings.env.config
        self.env = self.state.document.settings.env
        self.record_dependencies = \
            self.state.document.settings.record_dependencies
        location = os.path.normpath(
            os.path.join(self.env.srcdir,
                         self.config.cloudformationyaml_root
                         + '/' + self.arguments[0]))
        self.result = ViewList()
        #check file exists
        # should probably walk the filesystem here
        if os.path.isfile(location):
            self.parse_file(location)
        else:
            raise CloudformationYAMLException('%s:%s: location "%s" is not a file.' % (
                                    self.env.doc2path(self.env.docname, None),
                                    self.content_offset - 1,
                                    location))
        self.record_dependencies.add(location)
        node = nodes.paragraph()
        # parse comment internals as reST
        old_reporter = self.state.memo.reporter
        self.state.memo.reporter = AutodocReporter(
            self.result, self.state.memo.reporter)
        nested_parse_with_titles(self.state, self.result, node)
        self.state.memo.reporter = old_reporter
        return [node]

    def parse_file(self, source):
        """
        The file parser based on what the task runner finds

        :param source:
        :return: nothing
        :raise CloudformationYAMLException
        """
        with open(source, 'r') as stream:
            try:
                contents = ruamel.yaml.safe_load(stream)
            except Exception as exc:
                raise CloudformationYAMLException('%s:%s: source "%s" is not a valid YAML file.' % (
                    self.env.doc2path(self.env.docname, None),
                    self.content_offset - 1,
                    source))
        in_docstring = False
        return
        for linenum, line in enumerate(lines, start=1):
            if line.startswith(self.config.cloudformationyaml_comment):
                in_docstring = True
                self._parse_line(line, source, linenum)
            else:
                in_docstring = False
                # add terminating newline
                self._parse_line('', source, linenum)

    def _parse_line(self, line, source, linenum, starting=False):
        """
        Internal comment parsing routine
        :param line:
        :param source:
        :param linenum:
        :param starting:
        :return: appends comment to the result
        """
        docstring = line[len(self.config.cloudformationyaml_comment):]
        # strip preceding whitespace
        if docstring and docstring[0] == ' ':
            docstring = docstring[1:]
        self.result.append(docstring, source, linenum)


def setup(app):
    """
    The setup for the sphinx plugin

    :param app: A sphinx app is passed in here
    :return:
    """
    app.add_directive('cloudformationyaml', CloudformationYAMLDirective)
    app.add_config_value('cloudformationyaml_root', '..', 'env')
    app.add_config_value('cloudformationyaml_comment', '#', 'env')
