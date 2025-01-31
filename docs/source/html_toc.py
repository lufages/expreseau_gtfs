# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 11:40:57 2024

@author: Lucas
"""

from bs4 import BeautifulSoup
from docutils import nodes
from sphinx.util.docutils import SphinxDirective

class HTMLTOCDirective(SphinxDirective):
    required_arguments = 1  # Chemin du fichier HTML
    optional_arguments = 0
    has_content = False

    def run(self):
        file_path = self.arguments[0]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
        except FileNotFoundError:
            error = self.state_machine.reporter.error(
                f"HTML file '{file_path}' not found.",
                nodes.literal_block(self.block_text, self.block_text),
                line=self.lineno)
            return [error]

        # Récupérer les titres <h1>, <h2>, etc.
        toc = nodes.section()
        for level in range(1, 7):  # Pour les titres de <h1> à <h6>
            for header in soup.find_all(f'h{level}'):
                header_id = header.get('id', header.text.strip().replace(' ', '-').lower())
                title_node = nodes.title(text=header.text.strip())
                reference_node = nodes.reference('', '', refid=header_id)
                reference_node += title_node
                toc += reference_node

        return [toc]

def setup(app):
    app.add_directive('html_toc', HTMLTOCDirective)
