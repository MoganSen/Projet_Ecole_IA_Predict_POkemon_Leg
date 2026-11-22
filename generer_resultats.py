"""
Pre-calcule les 30 combinaisons de reglages du modele et les enregistre
dans un fichier JSON lu par le site.

A lancer depuis le dossier du projet, avec l'environnement virtuel actif :

    python generer_resultats.py

Produit : docs/data/resultats.json
"""

import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text

# --- Parametres identiques a ceux du notebook ---------------------------------

STATS = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
PROFONDEUR_MAX = 15
GRAINE = 42
PART_TEST = 0.2

racine = Path(__file__).parent
chemin_csv = racine / "public" / "Pokemon.csv"
chemin_sortie = racine / "docs" / "data" / "resultats.json"

if not chemin_csv.exists():
    sys.exit(f"Fichier introuvable : {chemin_csv}")

df = pd.read_csv(chemin_csv)
X = df[STATS]
y = df["Legendary"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=PART_TEST, stratify=y, random_state=GRAINE
)

noms_test = df.loc[X_test.index, "Name"].tolist()
verite_test = y_test.tolist()

# --- Repere : le modele qui repond toujours "non" -----------------------------

score_modele_bete = float((y_test == False).mean())

# --- Boucle sur les 30 combinaisons -------------------------------------------

combinaisons = {}

for pondere in (False, True):
    for profondeur in range(1, PROFONDEUR_MAX + 1):
        modele = DecisionTreeClassifier(
            max_depth=profondeur,
            class_weight="balanced" if pondere else None,
            random_state=GRAINE,
        ).fit(X_train, y_train)

        pred_train = modele.predict(X_train)
        pred_test = modele.predict(X_test)
        tn, fp, fn, tp = confusion_matrix(y_test, pred_test).ravel()

        trouves, manques, fausses_alertes = [], [], []
        for nom, vrai, predit in zip(noms_test, verite_test, pred_test):
            if vrai and predit:
                trouves.append(nom)
            elif vrai and not predit:
                manques.append(nom)
            elif not vrai and predit:
                fausses_alertes.append(nom)

        combinaisons[f"{profondeur}_{int(pondere)}"] = {
            "profondeur": profondeur,
            "pondere": pondere,
            "acc_train": round(float(accuracy_score(y_train, pred_train)), 5),
            "acc_test": round(float(accuracy_score(y_test, pred_test)), 5),
            "rec_train": round(
                float(recall_score(y_train, pred_train, pos_label=True)), 5
            ),
            "rec_test": round(
                float(recall_score(y_test, pred_test, pos_label=True)), 5
            ),
            "prec_train": round(
                float(
                    precision_score(
                        y_train, pred_train, pos_label=True, zero_division=0
                    )
                ),
                5,
            ),
            "prec_test": round(
                float(
                    precision_score(
                        y_test, pred_test, pos_label=True, zero_division=0
                    )
                ),
                5,
            ),
            "matrice": [int(tn), int(fp), int(fn), int(tp)],
            "profondeur_reelle": int(modele.get_depth()),
            "nb_feuilles": int(modele.get_n_leaves()),
            "regles": export_text(modele, feature_names=STATS),
            "trouves": trouves,
            "manques": manques,
            "fausses_alertes": fausses_alertes,
        }

# --- Profondeur a laquelle chaque arbre cesse de grandir ----------------------

arbres_libres = {}
for pondere in (False, True):
    libre = DecisionTreeClassifier(
        class_weight="balanced" if pondere else None, random_state=GRAINE
    ).fit(X_train, y_train)
    arbres_libres[int(pondere)] = int(libre.get_depth())

# --- Assemblage ---------------------------------------------------------------

# --- Les 800 Pokemon, pour le nuage de points du site ------------------------

index_test = set(X_test.index)
pokemon = [
    {
        "n": row["Name"],
        "s": [int(row[c]) for c in STATS],
        "l": bool(row["Legendary"]),
        "t": int(i in index_test),
    }
    for i, row in df.iterrows()
]

# --- Assemblage ---------------------------------------------------------------

resultat = {
    "pokemon": pokemon,
    "meta": {
        "total_pokemon": int(len(df)),
        "total_legendaires": int(y.sum()),
        "part_legendaires": round(float(y.mean()), 5),
        "n_train": int(len(X_train)),
        "legendaires_train": int(y_train.sum()),
        "n_test": int(len(X_test)),
        "legendaires_test": int(y_test.sum()),
        "score_modele_bete": round(score_modele_bete, 5),
        "stats": STATS,
        "graine": GRAINE,
        "profondeur_max": PROFONDEUR_MAX,
        "profondeur_naturelle": arbres_libres,
        "reglage_retenu": {"profondeur": 4, "pondere": True},
        "versions": {
            "pandas": pd.__version__,
            "scikit_learn": __import__("sklearn").__version__,
        },
    },
    "combinaisons": combinaisons,
}

chemin_sortie.parent.mkdir(parents=True, exist_ok=True)
chemin_sortie.write_text(
    json.dumps(resultat, ensure_ascii=False, separators=(",", ":")),
    encoding="utf-8",
)

taille_ko = chemin_sortie.stat().st_size / 1024
print(f"Ecrit : {chemin_sortie}  ({taille_ko:.0f} Ko, {len(combinaisons)} combinaisons)")

retenu = combinaisons["4_1"]
print(
    "Verification profondeur 4 ponderee -> "
    f"acc {retenu['acc_train']:.1%}/{retenu['acc_test']:.1%}  "
    f"rappel {retenu['rec_train']:.1%}/{retenu['rec_test']:.1%}  "
    f"precision {retenu['prec_train']:.1%}/{retenu['prec_test']:.1%}  "
    f"matrice {retenu['matrice']}"
)
