"""
Script pour mettre à jour les URLs d'administration dans les templates.
Ce script recherche et remplace toutes les occurrences de 'admin_custom.' par 'admin-custom.'
dans les templates pour refléter le changement de préfixe URL dans le blueprint.

À exécuter depuis le répertoire racine du projet.
"""

import os
import re

def update_templates():
    templates_dir = 'app/templates'
    pattern = r"url_for\('admin_custom\."
    replacement = r"url_for('admin-custom."
    
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                update_file(file_path, pattern, replacement)

def update_file(file_path, pattern, replacement):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Rechercher le pattern
    matches = re.findall(pattern, content)
    if matches:
        # Remplacer toutes les occurrences
        modified_content = re.sub(pattern, replacement, content)
        
        # Écrire les modifications dans le fichier
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        print(f"Mis à jour {file_path}: {len(matches)} occurrences")

if __name__ == "__main__":
    update_templates()
    print("Mise à jour des templates terminée.")
