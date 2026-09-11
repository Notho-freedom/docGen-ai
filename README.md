# docShadow CLI — Silent Companion for Git

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![CLI](https://img.shields.io/badge/CLI-Click-000000?logo=python&logoColor=white)](https://click.palletsprojects.com/)
[![Git](https://img.shields.io/badge/Git-GitPython-F05032?logo=git&logoColor=white)](https://git-scm.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**docShadow** (alias **GitShadow**) est un outil CLI qui génère automatiquement de la documentation JSON à chaque commit Git, conçu pour alimenter des interfaces UI avec une documentation de code structurée.

## 🎯 Objectif

docShadow est un "silent companion" de Git - un *shadow face* qui suit chaque commit sans intervention manuelle, générant automatiquement une documentation JSON complète de votre code Python.

## ✨ Fonctionnalités

- **🔄 Génération automatique** : Documentation créée à chaque commit via Git hooks
- **📊 Format JSON structuré** : Schéma standardisé pour intégration UI
- **🎯 Parsing AST intelligent** : Extraction complète des classes, fonctions, docstrings
- **🚫 Gestion des exclusions** : Support `.docignore` (basé sur `.gitignore`)
- **📁 Structure miroir** : Organisation calquée sur l'arborescence du projet
- **⚡ CLI simple** : 3 commandes principales (`init`, `generate`, `status`)

## 🚀 Installation

```bash
# Clone du repository
git clone <repo-url>
cd docGen-ai

# Installation des dépendances
pip install -r requirements.txt

# Installation en mode développement
pip install -e .
```

## 📖 Utilisation

### Initialisation

```bash
# Dans un repository Git existant
doc init
```

Cette commande :
- ✅ Crée `docshadow.config.json`
- ✅ Copie `.gitignore` vers `.docignore`
- ✅ Crée le dossier `.docshadow/`
- ✅ Installe le Git hook `post-commit`
- ✅ Ajoute `.docshadow/` au `.gitignore`

### Génération manuelle

```bash
# Générer pour le commit actuel
doc generate

# Générer pour un commit spécifique
doc generate --commit a1b2c3d
```

### Statut et informations

```bash
# Afficher l'état de docShadow
doc status
```

## 📁 Structure des fichiers générés

```
.docshadow/
├── index.json              # Résumé du commit courant
├── docshadow.json          # Mapping global du projet
└── module/                 # Structure miroir du code source
    ├── foo.py.json         # Documentation de module/foo.py
    └── bar.py.json         # Documentation de module/bar.py
```

### Exemples de schémas JSON

#### `index.json`
```json
{
  "commit": "a1b2c3d4e5f6",
  "short_commit": "a1b2c3d",
  "date": "2025-01-25T14:23:11Z",
  "message": "Add new feature",
  "author": "Developer <dev@example.com>",
  "files": ["module/foo.py.json", "module/bar.py.json"]
}
```

#### `docshadow.json`
```json
{
  "project": "MyAwesomeRepo",
  "generated_at": "2025-01-25T14:30:00Z",
  "commit": "a1b2c3d4e5f6",
  "structure": {
    "module": {
      "foo.py": "module/foo.py.json",
      "bar.py": "module/bar.py.json"
    }
  }
}
```

#### `module/foo.py.json`
```json
{
  "path": "module/foo.py",
  "module_docstring": "Module docstring...",
  "imports": [...],
  "classes": [
    {
      "name": "MyClass",
      "docstring": "Class description...",
      "line_number": 10,
      "methods": [...],
      "properties": [...]
    }
  ],
  "functions": [...],
  "constants": [...]
}
```

## ⚙️ Configuration

Le fichier `docshadow.config.json` permet de personnaliser le comportement :

```json
{
  "project_name": "MyAwesomeRepo",
  "languages": ["python"],
  "output_dir": ".docshadow/",
  "hooks": {
    "post_commit": true
  },
  "ignore": ".docignore"
}
```

## 🚫 Exclusions (.docignore)

Le fichier `.docignore` utilise la même syntaxe que `.gitignore` :

```
# Exclusions docShadow
__pycache__/
*.pyc
tests/
docs/
*.md
```

## 🔧 Développement

### Stack technique

- **Python 3.10+**
- **Click** : Framework CLI
- **GitPython** : Intégration Git
- **AST** : Parsing Python natif
- **pathspec** : Gestion patterns `.docignore`

### Architecture

```
docshadow/
├── __init__.py
├── __main__.py          # Point d'entrée CLI
├── commands/            # Commandes CLI
│   ├── init.py         # doc init
│   ├── generate.py     # doc generate
│   └── status.py       # doc status
├── generator.py         # Extraction AST + génération JSON
└── utils.py             # Utilitaires Git, fichiers, etc.
```

## 🗺️ Roadmap

- [x] **Prototype CLI** (init + hooks)
- [x] **Module generator.py** (parsing Python AST)
- [x] **Structure de sortie** (miroir du projet)
- [ ] **Envoi serveur distant** (après git push)
- [ ] **Support multi-langages** (JS, Java...)
- [ ] **Interface UI** (consommation JSON)
- [ ] **Tests unitaires**

## 📝 Licence

MIT License

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir des issues ou proposer des pull requests.

---

**docShadow** - *Votre companion silencieux pour une documentation toujours à jour* 🌟
