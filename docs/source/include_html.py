# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 11:08:31 2024

@author: Lucas
"""

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective

class IncludeHTML(SphinxDirective):
    required_arguments = 1  # Chemin du fichier HTML
    has_content = False

    def run(self):
        file_path = self.arguments[0]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except FileNotFoundError:
            error = self.state_machine.reporter.error(
                f"HTML file '{file_path}' not found.",
                nodes.literal_block(self.block_text, self.block_text),
                line=self.lineno)
            return [error]

        raw_node = nodes.raw('', html_content, format='html')
        return [raw_node]

def setup(app):
    app.add_directive('include_html', IncludeHTML)
