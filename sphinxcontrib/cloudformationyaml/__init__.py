import os

from docutils.statemachine import ViewList
from docutils.parsers.rst import Directive
from docutils import nodes
from sphinx.util.nodes import nested_parse_with_titles
from sphinx.ext.autodoc import AutodocReporter


class CloudformationYAMLException(Exception):
    pass


class CloudformationYAMLDirective(Directive):

    required_arguments = 1

    def run(self):
        self.config = self.state.document.settings.env.config
        self.env = self.state.document.settings.env
        self.record_dependencies = \
            self.state.document.settings.record_dependencies
        location = os.path.normpath(
            os.path.join(self.env.srcdir,
                         self.config.cloudformationyaml_root
                         + '/' + self.arguments[0]))
        self.result = ViewList()
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
        with open(source, 'r') as src:
            lines = src.read().splitlines()
        in_docstring = False
        for linenum, line in enumerate(lines, start=1):
            if line.startswith(self.config.cloudformationyaml_comment):
                in_docstring = True
                self._parse_line(line, source, linenum)
            else:
                in_docstring = False
                # add terminating newline
                self._parse_line('', source, linenum)

    def _parse_line(self, line, source, linenum, starting=False):
        docstring = line[len(self.config.cloudformationyaml_comment):]
        # strip preceding whitespace
        if docstring and docstring[0] == ' ':
            docstring = docstring[1:]
        self.result.append(docstring, source, linenum)


def setup(app):
    app.add_directive('cloudformationyaml', CloudformationYAMLDirective)
    app.add_config_value('cloudformationyaml_root', '..', 'env')
    app.add_config_value('cloudformationyaml_comment', '#', 'env')
