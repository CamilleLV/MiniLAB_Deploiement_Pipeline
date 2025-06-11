# 🛠️ Mini Lab - Déploiement de Pipeline (German Credit Data)

Ce projet constitue un pipeline de traitement de données basé sur le dataset [Statlog (German Credit Data)](https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data).  
Il inclut les étapes suivantes :

- 📥 Téléchargement des données depuis UCI
- 🔄 Transformation et nettoyage
- ☁️ Upload dans MinIO
- 🗄️ Chargement dans une base SQLite
- ⚙️ Orchestration via Apache Airflow

---

## 🚀 Prérequis

- Python 3.10+
- `pip`, `venv`
- MinIO installé localement (sans Docker)
- Airflow 2.8+ (facultatif pour l’orchestration)

---

## 🔧 Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-utilisateur/nom-du-repo.git
cd nom-du-repo

# 2. Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 3. Installer les dépendances
pip install -r requirements.txt
