# Prédire si un Pokémon est légendaire

Un notebook marimo interactif qui entraîne un **arbre de décision** à
reconnaître les Pokémon légendaires à partir de leurs six statistiques de
combat — et qui s'en sert pour illustrer le surapprentissage, le déséquilibre
des classes et le compromis rappel / précision.

**▶️ [Essayer le notebook en ligne](#)** *(lien à venir)*

> Travail réalisé dans le cadre du cours « Fondamentaux de l'IA et bonnes
> pratiques », séance 2 — Mastère 1 Cybersécurité, OTERIA, novembre 2026.

---

## Le problème

Le jeu de données compte 800 Pokémon, dont seulement **65 légendaires** (8 %).
Ce déséquilibre est le cœur de l'exercice : un programme qui répondrait « non »
à chaque question obtiendrait déjà **91,9 %** de bonnes réponses sans rien
comprendre.

C'est la structure exacte d'un problème de détection d'intrusion : repérer les
quelques événements dangereux noyés dans une masse d'événements normaux.

## Résultat

Modèle retenu : arbre de décision de profondeur 4, avec pondération des classes.

| Mesure | Entraînement | Test |
| --- | --- | --- |
| Accuracy | 92,5 % | 89,4 % |
| Rappel | 100,0 % | 76,9 % |
| Précision | 52,0 % | 41,7 % |

Sur les 13 légendaires jamais vus par le modèle, il en retrouve **10**, au prix
de 14 fausses alertes sur 147 Pokémon normaux.

La règle principale apprise par l'arbre, lisible telle quelle :
`Sp. Atk > 89` **et** `Attack > 84,5` **et** `Speed > 69`.

## Ce que les expériences ont montré

**L'accuracy peut mentir.** Le modèle retenu affiche 89,4 % d'accuracy, soit
*moins* que le programme qui répond toujours « non ». Il est pourtant cinq fois
meilleur pour trouver ce qu'on cherche.

**Plus complexe n'est pas meilleur.** En passant de la profondeur 1 à 15,
l'accuracy d'entraînement grimpe de 91,9 % à 99,8 % sans que celle de test
progresse. Tout le gain part en mémorisation — et la trace est visible dans
l'arbre, qui déclare « légendaire » sur une fenêtre de vitesse large de
1,5 point.

**Le bon réglage dépend du coût des erreurs.** Activer la pondération fait
passer le rappel de 15 % à 77 % et la précision de 100 % à 38 %. Arbitrer entre
les deux est une décision métier, pas un choix technique.

**Les données ont leurs propres défauts.** Six Pokémon partagent des
statistiques identiques avec des étiquettes contradictoires, ce qui impose un
plancher d'erreur infranchissable. Et parmi les 14 « fausses » alertes du modèle
retenu, trois concernent des Pokémon réellement légendaires que le jeu de
données classe à tort.

## Lancer le notebook en local

```powershell
git clone https://github.com/MoganSen/Projet_M1C_IA_PredictPOKE.git
cd Projet_M1C_IA_PredictPOKE
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
marimo edit pokemon.py
```

Sous Windows, si l'activation est refusée avec « l'exécution de scripts est
désactivée » :

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Sous macOS ou Linux, remplacer la ligne d'activation par
`source .venv/bin/activate`.

## Contenu du dépôt

| Fichier | Rôle |
| --- | --- |
| `pokemon.py` | Le notebook marimo — un notebook marimo est un simple fichier Python, donc lisible et comparable directement sur GitHub |
| `Pokemon.csv` | Les données |
| `requirements.txt` | Les versions exactes des bibliothèques |

## Données

[Pokemon with stats](https://www.kaggle.com/datasets/abcsds/pokemon) — Kaggle,
publié par *abcsds*. 800 lignes, 13 colonnes : les 721 numéros du Pokédex
auxquels s'ajoutent les méga-évolutions et les formes alternatives.

## Limites assumées

- Le réglage a été choisi en consultant le jeu de test, qui ne constitue donc
  plus une estimation honnête. La méthode correcte serait la validation croisée
  sur le seul jeu d'entraînement.
- Le jeu de test ne contient que 13 légendaires : chacun pèse 7,7 points de
  rappel, et une partie des écarts observés relève du bruit statistique.
- Seules les six statistiques de base sont utilisées ; le type, la génération et
  le total ne sont pas exploités.

## Utilisation de l'IA

Une IA a été utilisée comme aide pour le design et le code du notebook, la
compréhension du projet et la rédaction du README.

## Auteur

MoganSen — Mastère 1 Cybersécurité, OTERIA.
