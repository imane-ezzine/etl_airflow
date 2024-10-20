import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from warnings import simplefilter
from flask import Flask, request, jsonify

# Ignore les avertissements UserWarning
simplefilter(action='ignore', category=UserWarning)

# Fonction de prédiction utilisant un modèle Gradient Boosting Regressor
def gradient_boosting(hospitalized_now: int):
    # Lecture du fichier CSV avec les données
    df = pd.read_csv("clean_covid_data.csv", index_col=[0])
    df = df.dropna()

    # Sélection des colonnes
    x = df[["hospitalizedCurrently"]]
    y = df["deathIncrease"]

    # Division des données en ensemble d'entraînement et de test
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, shuffle=True)
    
    # Création et entraînement du modèle
    model = GradientBoostingRegressor(n_estimators=250, learning_rate=0.01, min_samples_leaf=20)
    model.fit(x_train, y_train)

    # Prédiction de l'augmentation des décès
    return round(model.predict([[hospitalized_now]])[0], 2)

# Création de l'application Flask
app = Flask(__name__)

# Route pour la page d'accueil
@app.route('/')
def index():
    return "Bienvenue sur l'API COVID-19. Utilisez /predict/<hospitalized_now> pour obtenir des prédictions."

# Route pour prédire l'augmentation des décès
@app.route('/predict/<int:hospitalized_now>', methods=['GET'])
def predict(hospitalized_now):
    try:
        # Appel de la fonction de prédiction
        death_increase = gradient_boosting(hospitalized_now)
        return jsonify({
            "death_increase": death_increase
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route pour éviter les erreurs favicon.ico
@app.route('/favicon.ico')
def favicon():
    return "", 204  # No Content

# Lancement de l'application Flask
if __name__ == '__main__':
    app.run(port=5000)
