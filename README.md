# SMART WATER AI
Plateforme de supervision intelligente des réseaux d'eau (projet universitaire, données fictives).

## Démarrage (étape 1)
python -m venv venv
venv\Scripts\activate        (Windows)  |  source venv/bin/activate (Linux/macOS)
pip install -r requirements.txt
copier .env.example vers .env et renseigner SECRET_KEY / DATABASE_URL
python app.py
