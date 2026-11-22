import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(r"""
    # Prédire si un Pokémon est légendaire

    **MoganSen** Mastère 1 Cybersécurité, OTERIA
    Cours « Fondamentaux de l'IA et bonnes pratiques », séance 2 novembre 2026

    ---

    Ce notebook entraîne un **arbre de décision** à reconnaître un Pokémon
    légendaire à partir de ses six statistiques de combat : points de vie, attaque,
    défense, attaque spéciale, défense spéciale et vitesse.

    Le jeu de données contient 800 Pokémon, dont seulement **65 légendaires**, soit
    8 % du total. Ce fort déséquilibre est le cœur du problème : un programme qui
    répondrait « non » à chaque question obtiendrait déjà 91,9 % de bonnes réponses
    sans rien comprendre. Tout l'enjeu consiste donc à mesurer la performance
    autrement que par le simple taux de réussite.

    C'est le même problème que la détection d'intrusion en cybersécurité : repérer
    les quelques événements dangereux noyés dans une masse d'événements normaux.

    **Comment utiliser ce notebook** — le curseur et la case à cocher de la
    section 4 règlent le modèle en direct. Tous les résultats affichés plus bas se
    recalculent automatiquement. La section 7 présente les expériences menées avec
    ces deux réglages et leur interprétation.

    *Jeu de données : [Pokemon with stats](https://www.kaggle.com/datasets/abcsds/pokemon) — Kaggle, abcsds.*
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 1. Les données

    On charge le fichier `Pokemon.csv` et on regarde à quoi il ressemble.
    """)
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import altair as alt

    return alt, mo, pd


@app.cell
def _(mo, pd):
    chemin_csv = mo.notebook_location() / "public" / "Pokemon.csv"
    # En ligne, on télécharge d'abord le fichier : GitHub Pages le compresse
    # pendant le transfert, et pandas tenterait de le décompresser une 2e fois.
    if str(chemin_csv).startswith("http"):
        import io as _io
        import urllib.request as _requete

        with _requete.urlopen(str(chemin_csv)) as _reponse:
            df = pd.read_csv(_io.BytesIO(_reponse.read()))
    else:
        df = pd.read_csv(chemin_csv)
    df
    return (df,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 2. Explorer les données

    Avant d'entraîner quoi que ce soit, on regarde la forme des statistiques, la
    répartition de ce qu'on cherche à prédire, et on visualise les légendaires par
    rapport aux autres. Les deux menus déroulants permettent de choisir les axes.
    """)
    return


@app.cell
def _(df):
    df.describe().round(1)
    return


@app.cell
def _(df):
    df["Legendary"].value_counts()
    return


@app.cell
def _(mo):
    stats = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
    axe_x = mo.ui.dropdown(options=stats, value="Attack", label="Axe X")
    axe_y = mo.ui.dropdown(options=stats, value="Sp. Atk", label="Axe Y")
    mo.hstack([axe_x, axe_y])
    return axe_x, axe_y, stats


@app.cell
def _(alt, axe_x, axe_y, df):
    # Les points sont écrits directement dans le graphique pour qu'il s'affiche
    # aussi dans la version en ligne du notebook.
    _points = [
        {"Name": _nom, "x": int(_x), "y": int(_y), "Legendary": str(bool(_legendaire))}
        for _nom, _x, _y, _legendaire in zip(
            df["Name"], df[axe_x.value], df[axe_y.value], df["Legendary"]
        )
    ]
    alt.Chart(alt.Data(values=_points)).mark_circle(size=40, opacity=0.6).encode(
        x=alt.X("x:Q", title=axe_x.value),
        y=alt.Y("y:Q", title=axe_y.value),
        color=alt.Color("Legendary:N", title="Legendary"),
        tooltip=[
            alt.Tooltip("Name:N", title="Nom"),
            alt.Tooltip("x:Q", title=axe_x.value),
            alt.Tooltip("y:Q", title=axe_y.value),
        ],
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. Préparer les données

    On sépare les **entrées** du modèle (`X`, les six statistiques) de la **réponse
    à prédire** (`y`, la colonne `Legendary`). Puis on met 20 % des Pokémon de côté :
    le modèle ne les verra jamais pendant son entraînement, ils serviront à le noter
    honnêtement. L'option `stratify` garantit que la proportion de légendaires reste
    la même des deux côtés.
    """)
    return


@app.cell
def _():
    from sklearn.model_selection import train_test_split

    return (train_test_split,)


@app.cell
def _(df, stats):
    X = df[stats]
    y = df["Legendary"]
    return X, y


@app.cell
def _(X, mo, train_test_split, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    mo.md(f"**Entraînement** : {len(X_train)} Pokémon dont {y_train.sum()} légendaires  \n"
          f"**Test** : {len(X_test)} Pokémon dont {y_test.sum()} légendaires")
    return X_test, X_train, y_test, y_train


@app.cell
def _(mo):
    mo.md(r"""
    ## 4. Entraîner le modèle

    Le curseur fixe le nombre maximal de questions que l'arbre peut poser en
    cascade. La case à cocher change le barème : elle rend les erreurs sur les
    légendaires beaucoup plus coûteuses que les erreurs sur les Pokémon normaux.

    Ces deux réglages sont des **hyperparamètres** : je les choisis moi-même, par
    opposition aux seuils de l'arbre, que le modèle apprend seul à partir des
    données.
    """)
    return


@app.cell
def _(mo):
    profondeur = mo.ui.slider(1, 15, value=4, label="Profondeur max de l'arbre", show_value=True)
    equilibre = mo.ui.checkbox(value=True, label="Donner plus de poids aux légendaires")
    mo.vstack([profondeur, equilibre])
    return equilibre, profondeur


@app.cell
def _():
    from sklearn.tree import DecisionTreeClassifier, export_text

    return DecisionTreeClassifier, export_text


@app.cell
def _(DecisionTreeClassifier, X_train, equilibre, profondeur, y_train):
    modele = DecisionTreeClassifier(
        max_depth=profondeur.value,
        class_weight="balanced" if equilibre.value else None,
        random_state=42,
    )
    modele.fit(X_train, y_train)
    return (modele,)


@app.cell
def _(export_text, modele, stats):
    print(export_text(modele, feature_names=stats))
    return


@app.cell
def _(X_test, df, modele, y_test):
    resultats = df.loc[X_test.index, ["Name"]].assign(
        Vrai=y_test, Predit=modele.predict(X_test)
    )
    resultats
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 5. Évaluer le modèle

    Quatre mesures, dans un ordre qui compte. L'**accuracy** est la part de bonnes
    réponses — on la compare au score d'un programme qui répondrait toujours
    « non ». La **matrice de confusion** détaille les quatre cas possibles. Le
    **rappel** est la part des légendaires effectivement trouvés, et la
    **précision** la part des alertes qui sont justes.
    """)
    return


@app.cell
def _():
    from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix

    return accuracy_score, confusion_matrix, precision_score, recall_score


@app.cell
def _(X_test, X_train, accuracy_score, mo, modele, y_test, y_train):
    pred_train = modele.predict(X_train)
    pred_test = modele.predict(X_test)
    mo.md(f"""
    **Accuracy entraînement** : {accuracy_score(y_train, pred_train):.1%}  
    **Accuracy test** : {accuracy_score(y_test, pred_test):.1%}  
    **Modèle bête qui répond toujours « non »** : {(y_test == False).mean():.1%}
    """)
    return pred_test, pred_train


@app.cell
def _(confusion_matrix, pd, pred_test, y_test):
    pd.DataFrame(
        confusion_matrix(y_test, pred_test),
        index=["Vrai : normal", "Vrai : légendaire"],
        columns=["Prédit : normal", "Prédit : légendaire"],
    )
    return


@app.cell
def _(mo, precision_score, pred_test, recall_score, y_test):
    mo.md(f"""
    **Rappel** : {recall_score(y_test, pred_test, pos_label=True):.1%}  
    **Précision** : {precision_score(y_test, pred_test, pos_label=True):.1%}
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 6. Tableau de bord

    Les six mesures d'un coup, en entraînement et en test. L'écart entre les deux
    colonnes est l'indicateur à surveiller : plus il se creuse, plus le modèle
    apprend par cœur au lieu de comprendre.
    """)
    return


@app.cell
def _(
    accuracy_score,
    equilibre,
    mo,
    precision_score,
    pred_test,
    pred_train,
    profondeur,
    recall_score,
    y_test,
    y_train,
):
    mo.vstack([
        profondeur,
        equilibre,
        mo.md(f"""
    |  | Entraînement | Test |
    |---|---|---|
    | **Accuracy** | {accuracy_score(y_train, pred_train):.1%} | {accuracy_score(y_test, pred_test):.1%} |
    | **Rappel** | {recall_score(y_train, pred_train, pos_label=True):.1%} | {recall_score(y_test, pred_test, pos_label=True):.1%} |
    | **Précision** | {precision_score(y_train, pred_train, pos_label=True, zero_division=0):.1%} | {precision_score(y_test, pred_test, pos_label=True, zero_division=0):.1%} |
    """),
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 7. Mes expériences

    Trois expériences menées avec le curseur et la case à cocher, puis leur
    interprétation.

    *Les résultats en ligne peuvent légèrement varier pour les arbres profonds,
    car le navigateur utilise d'autres versions des bibliothèques.*
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Expérience 1 — Que fait la profondeur de l'arbre ?

    Case de pondération **décochée**, profondeur variable de 1 à 15.

    | Profondeur | Acc. entraînement | Acc. test | Rappel test | Précision test |
    | --- | --- | --- | --- | --- |
    | 1 | 91,9 % | 91,9 % | 0,0 % | 0,0 % |
    | 2 | 93,8 % | 93,8 % | 53,8 % | 63,6 % |
    | 3 | 95,3 % | 93,1 % | 15,4 % | 100,0 % |
    | 5 | 97,0 % | 91,9 % | 46,2 % | 50,0 % |
    | 7 | 99,4 % | 93,1 % | 53,8 % | 58,3 % |
    | 10 | 99,8 % | 92,5 % | 46,2 % | 54,5 % |
    | 15 | 99,8 % | 92,5 % | 46,2 % | 54,5 % |

    ### Ce que montrent ces chiffres

    **Le surapprentissage.** La colonne d'entraînement monte sans discontinuer, de
    91,9 % à 99,8 %. La colonne de test ne dépasse jamais 93,8 %, atteint dès la
    profondeur 2. Toute la complexité ajoutée ensuite n'a servi qu'à mémoriser le
    jeu d'entraînement.

    **L'accuracy masque le problème.** À la profondeur 7, l'écart entre les deux
    colonnes n'est que de 6,3 points sur l'accuracy, mais de 40 points sur le
    rappel. Quand la classe recherchée ne représente que 8 % des données, elle pèse
    trop peu dans l'accuracy pour la faire bouger. Le rappel, lui, ne regarde que
    les légendaires : il dit la vérité.

    **Plus profond n'est pas plus performant.** La profondeur 2 trouve 53,8 % des
    légendaires, la profondeur 3 seulement 15,4 %. Chaque feuille de l'arbre vote à
    la majorité ; en descendant d'un niveau, les feuilles rapetissent et basculent
    du côté « normal », qui représente 92 % des Pokémon. Ajouter de la profondeur
    peut donc détruire du rappel.

    **Le modèle le plus simple gagne.** À la profondeur 7, le rappel de test est
    identique à celui de la profondeur 2, avec une précision moins bonne. Mais
    l'arbre de profondeur 2 tient en une règle lisible, alors que celui de
    profondeur 7 a des dizaines de branches invérifiables. À performance égale sur
    des données nouvelles, on choisit le modèle explicable.

    ### Deux observations sur les données elles-mêmes

    **L'arbre s'arrête tout seul à 8 niveaux.** Au-delà, les résultats sont figés :
    l'arbre a fini de découper, il ne reste plus rien à séparer. `max_depth` ne
    contraint donc plus rien. Un hyperparamètre n'agit que tant qu'il est la
    contrainte qui mord.

    **L'accuracy d'entraînement plafonne à 99,8 % et non à 100 %.** Six Pokémon du
    jeu de données ont exactement les mêmes six statistiques — 100 partout : Mew,
    Celebi, Jirachi, Manaphy, Shaymin et Victini. Or la colonne `Legendary` les
    classe de façon contradictoire : trois à `True`, trois à `False`. Entrées
    identiques, réponses différentes : aucun algorithme ne peut les séparer. C'est
    une **erreur irréductible**, imposée par les données et non par le modèle, et
    elle révèle ici une incohérence d'étiquetage du jeu de données.

    **Conclusion de l'expérience 1 :** le meilleur réglage sans pondération est la
    profondeur 2, mais son rappel plafonne à 53,8 %. Le modèle rate encore la
    moitié des légendaires. La profondeur seule ne corrige pas le déséquilibre des
    classes — d'où l'expérience suivante.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Expérience 2 — Que fait la pondération des classes ?

    Profondeur fixée à **3**, case **cochée** puis décochée, pour comparer à
    réglage identique.

    | Profondeur 3 | Sans pondération | Avec pondération |
    | --- | --- | --- |
    | Accuracy test | 93,1 % | 88,1 % |
    | Rappel test | 15,4 % | 76,9 % |
    | Précision test | 100,0 % | 38,5 % |
    | Légendaires trouvés | 2 sur 13 | 10 sur 13 |
    | Fausses alertes | 0 | 16 |

    ### Ce que montrent ces chiffres

    **Le résultat le plus important de tout le TP.** Le rappel passe de 15,4 % à
    76,9 % : le modèle trouve cinq fois plus de légendaires. Et pendant ce temps,
    son accuracy **baisse** de 5 points.

    Autrement dit : le modèle devient radicalement plus utile, et la mesure la plus
    connue annonce une dégradation. Pour un jeu de données déséquilibré, l'accuracy
    n'est pas seulement insuffisante — elle peut conduire à rejeter le bon modèle.

    **Comment ça marche.** `class_weight="balanced"` attribue à chaque classe un
    poids inversement proportionnel à sa fréquence. Il y a environ onze fois plus de
    Pokémon normaux que de légendaires, donc rater un légendaire coûte à l'arbre à
    peu près autant que se tromper sur onze normaux. Ni le modèle ni les données
    n'ont changé : **c'est le barème qui a changé.** L'arbre, qui cherche toujours à
    minimiser son coût total, se met naturellement à prendre des risques.

    On le voit dans la structure même de l'arbre : sans pondération, sa première
    question est `Sp. Atk <= 114,5` ; avec pondération, elle devient
    `Sp. Atk <= 89,0`. Même critère, seuil abaissé — le modèle accepte beaucoup plus
    de candidats.

    **Le compromis rappel / précision, en chiffres.** On a gagné 8 légendaires et
    payé 16 fausses alertes. Quand l'un monte, l'autre baisse : c'est le compromis
    fondamental de toute détection.

    ### Pourquoi ce choix dépend du contexte

    Pour un Pokédex, l'affaire est excellente : une fausse alerte ne coûte rien, on
    vérifie la fiche et on passe à la suivante.

    Pour un détecteur d'intrusion, la lecture change. 16 fausses alertes sur 147
    événements normaux représentent environ 11 % de bruit. Sur un SOC qui traite des
    millions d'événements par jour, cela produit des dizaines de milliers d'alertes
    inutiles : les analystes décrochent et finissent par ignorer l'outil — c'est
    l'*alert fatigue*, une cause classique d'incident non détecté.

    **Il n'existe donc pas de « meilleur modèle » dans l'absolu.** Le bon réglage
    dépend du coût relatif des deux types d'erreur — rater une attaque contre
    déclencher une fausse alerte. C'est une décision métier, pas un choix technique.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Expérience 3 — Quel est le meilleur réglage ?

    **Critère fixé avant de regarder les résultats :** obtenir le rappel de test le
    plus élevé possible, parmi les réglages dont la précision de test atteint au
    moins 33 % — c'est-à-dire « rater le moins d'attaques possible, sans noyer
    l'analyste sous les fausses alertes ».

    Fixer le critère d'abord évite de choisir simplement le plus joli chiffre du
    tableau, ce qui n'est pas la même chose que choisir le meilleur modèle.

    Case cochée sur toute l'expérience.

    | Profondeur | Acc. entraînement | Acc. test | Rappel test | Précision test |
    | --- | --- | --- | --- | --- |
    | 1 | 77,5 % | 73,8 % | 84,6 % | 21,6 % |
    | 2 | 86,1 % | 83,1 % | 84,6 % | 30,6 % |
    | 3 | 90,3 % | 88,1 % | 76,9 % | 38,5 % |
    | 4 | 92,5 % | 89,4 % | 76,9 % | **41,7 %** |
    | 5 | 95,6 % | 90,6 % | 69,2 % | 45,0 % |
    | 6 | 97,8 % | 93,1 % | 61,5 % | 57,1 % |

    ### Application du critère

    Les profondeurs 1 et 2 sont éliminées : leur précision, 21,6 % et 30,6 %, passe
    sous le seuil fixé. Parmi les réglages restants, le rappel maximal est de
    76,9 %, atteint à égalité par les profondeurs 3 et 4. Le départage se fait sur
    la précision, meilleure à la profondeur 4.

    **Réglage retenu : profondeur 4, pondération activée.** La profondeur 3 reste
    une alternative défendable, légèrement moins précise mais plus simple.

    **Le critère détermine la réponse.** Avec un seuil de précision à 30 % au lieu
    de 33 %, c'est la profondeur 2 qui l'emportait, avec un rappel de 84,6 %. C'est
    pourquoi le critère doit être énoncé et justifié avant l'expérience, pas après.

    À noter également : la profondeur 6 affiche la meilleure accuracy de test du
    tableau (93,1 %) et se classe **dernière** sur le rappel. Une dernière
    illustration de la mesure trompeuse.

    ### Résultat du modèle retenu

    | Mesure | Entraînement | Test |
    | --- | --- | --- |
    | Accuracy | 92,5 % | 89,4 % |
    | Rappel | 100,0 % | 76,9 % |
    | Précision | 52,0 % | 41,7 % |

    Matrice de confusion sur les 160 Pokémon de test :

    |  | Prédit : normal | Prédit : légendaire |
    | --- | --- | --- |
    | **Vrai : normal** | 133 | 14 |
    | **Vrai : légendaire** | 3 | 10 |

    **Les 10 légendaires trouvés** — Articuno, Moltres, Mewtwo Mega X, Palkia,
    Darkrai, Deoxys, Cobalion, Thundurus Therian, Landorus Therian, Xerneas.

    **Les 3 manqués** — Regirock, Zygarde 50 %, Diancie.

    **Les 14 fausses alertes** — Kingdra, Mew, Carbink, Gardevoir Mega, Houndoom,
    Houndoom Mega, Umbreon, Magmortar, Manaphy, Metagross, Cresselia, Salamence,
    Arcanine, Sharpedo.

    ### Quand le modèle a raison et la donnée a tort

    Parmi ces 14 « fausses » alertes, **Mew, Manaphy et Cresselia sont légendaires
    ou fabuleux dans les jeux Pokémon.** C'est le jeu de données qui les étiquette
    `False`. En corrigeant ces trois lignes, la précision passerait de 41,7 % à
    environ 54 %.

    C'est le prolongement direct de l'incohérence relevée en expérience 1 : ce jeu
    de données traite les Pokémon fabuleux de façon contradictoire. Une partie des
    erreurs attribuées au modèle sont en réalité des erreurs d'étiquetage.

    ### Lecture des règles apprises

    Les règles affichées plus haut par `export_text` se lisent à trois niveaux.

    **La règle principale, celle qu'on peut énoncer à voix haute :** un Pokémon est
    déclaré légendaire s'il a `Sp. Atk > 89`, `Attack > 84,5` et `Speed > 69`.
    Fort en attaque spéciale, fort en attaque, et rapide. C'est exactement le profil
    attendu, et le modèle l'a trouvé seul.

    **Une trace visible de surapprentissage.** La branche `Speed > 107` suivie de
    `Speed <= 108,5 → légendaire` déclare « légendaire » sur une fenêtre de vitesse
    large de 1,5 point. Ce n'est pas une règle générale : c'est un individu précis du
    jeu d'entraînement que l'arbre a entouré au crayon. Le surapprentissage n'est
    donc pas une abstraction, il se montre du doigt.

    **Deux questions inutiles.** `Attack <= 15` répond `False` des deux côtés, et
    `Sp. Def <= 73` répond `True` des deux côtés. L'arbre les a posées parce
    qu'elles rendaient les groupes plus homogènes, pas parce qu'elles changent la
    décision finale.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Conclusion et limites

    ### Ce que ce travail a montré

    Un arbre de décision entraîné sur les six statistiques de base reconnaît un
    Pokémon légendaire dans **77 % des cas**, au prix d'une fausse alerte sur dix
    Pokémon normaux. Le modèle a découvert seul le profil attendu — fort en attaque
    spéciale, fort en attaque, rapide — sans qu'on lui souffle la moindre règle.

    Mais le résultat le plus instructif n'est pas cette performance. Il tient en
    trois constats.

    **1. Une mesure populaire peut mentir.** Le modèle final affiche 89,4 %
    d'accuracy, soit *moins* qu'un programme qui répondrait « non » à chaque
    question (91,9 %). Il est pourtant incomparablement plus utile. Quand la classe
    recherchée est rare, l'accuracy est dominée par la classe majoritaire et ne dit
    plus rien de ce qui compte.

    **2. Plus complexe n'est pas meilleur.** L'accuracy d'entraînement est montée de
    91,9 % à 99,8 % sans que celle de test progresse. Tout ce gain est allé dans la
    mémorisation. Un arbre de profondeur 2, lisible en une phrase, égale un arbre de
    profondeur 7 sur des données nouvelles.

    **3. Le réglage dépend du coût des erreurs, pas de la technique.** Activer la
    pondération échange de la précision contre du rappel. Le bon arbitrage se décide
    en fonction de ce que coûte un oubli face à ce que coûte une fausse alerte — une
    question métier.

    ### Transposition à la cybersécurité

    Le problème traité ici est structurellement celui de la détection d'intrusion :
    une classe rare et dangereuse noyée dans une masse d'événements normaux.

    Le rappel correspond à la part des attaques effectivement détectées, la
    précision à la part des alertes qui ne sont pas des fausses alertes. Un
    détecteur à 100 % de précision et 15 % de rappel — notre arbre de profondeur 3
    sans pondération — ne déclenche jamais à tort et laisse passer 85 % des
    intrusions. À l'inverse, un détecteur trop permissif noie l'équipe sous le bruit
    et finit par être ignoré : c'est l'*alert fatigue*. Le réglage du curseur de ce
    notebook est, à petite échelle, le réglage d'un seuil de détection.

    ### Limites de ce travail

    **Le jeu de test a servi à choisir le réglage.** Ayant été consulté une dizaine
    de fois pour comparer les configurations, il ne constitue plus une estimation
    honnête de la performance sur des données réellement nouvelles. La méthode
    correcte est la **validation croisée** sur le seul jeu d'entraînement, le jeu de
    test n'étant ouvert qu'une fois, à la toute fin. Cette limite est assumée.

    **Le jeu de test est petit.** Il ne contient que 13 légendaires. Chacun pèse
    donc 7,7 points de rappel : un seul Pokémon classé différemment fait bouger le
    résultat de façon spectaculaire. C'est ce qui explique l'allure heurtée des
    chiffres de l'expérience 1, où le rappel monte et descend sans régularité. Ces
    écarts sont en partie du bruit statistique, et non de véritables différences
    entre les modèles.

    **Les étiquettes sont imparfaites.** Le jeu de données classe les Pokémon
    fabuleux de façon contradictoire, ce qui impose un plancher d'erreur
    infranchissable et fausse la précision mesurée.

    **Les entrées sont volontairement limitées.** Seules les six statistiques de
    base ont été utilisées. Le type, la génération et le total n'ont pas été
    exploités, alors qu'ils porteraient sans doute de l'information.

    ### Pistes de prolongement

    - Régler les hyperparamètres par **validation croisée** plutôt qu'en consultant
      le jeu de test.
    - Tracer la **courbe de surapprentissage** : scores d'entraînement et de test en
      fonction de la profondeur, sur un même graphique.
    - Comparer l'arbre à d'autres modèles — forêt aléatoire, k plus proches
      voisins, régression logistique.
    - Rejouer la démarche sur un **jeu de données de cybersécurité** réel, par
      exemple Phishing Websites puis NSL-KDD, où le déséquilibre des classes et le
      compromis rappel / précision se posent dans les mêmes termes.
    """)
    return


if __name__ == "__main__":
    app.run()
