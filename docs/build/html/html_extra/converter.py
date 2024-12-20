# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 11:46:36 2024

@author: Lucas
"""

import os
from bs4 import BeautifulSoup

def generate_rst_from_html(html_dir, output_dir):
    for filename in os.listdir(html_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(html_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')

            toc_content = []
            for level in range(1, 7):
                for header in soup.find_all(f'h{level}'):
                    title = header.text.strip()
                    header_id = header.get('id', title.replace(' ', '-').lower())
                    toc_content.append(f"{'  ' * (level - 1)}* `{title} <#{header_id}>`_")

            # Créez le fichier RST
            rst_filename = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.rst")
            with open(rst_filename, 'w', encoding='utf-8') as rst_file:
                rst_file.write(f"{filename}\n{'=' * len(filename)}\n\n")
                rst_file.write(".. raw:: html\n\n")
                rst_file.write(f"    <iframe src='{filename}' width='100%' height='800px'></iframe>\n\n")
                rst_file.write("Table of Contents\n")
                rst_file.write("-----------------\n\n")
                rst_file.write("\n".join(toc_content))

# Exemple d'utilisation


source = r"C:\Users\Lucas\Documents\python_libs_perso\expreseau_gtfs\expreseau_gtfs\build\html\html_extra"

generate_rst_from_html(source, source)
