# Overcooked Multijoueur Coop — Projet POA

Simulation graphique inspirée du jeu **Overcooked**, développée en **Python / Tkinter** dans le cadre du module POA (Programmation Orientée Agents/Objet).
Deux agents cuisiniers (`ChefAgent`) préparent des plats à partir de recettes définies, seuls ou en coopération, avec chronomètre et mode de test automatisé.

---

## Structure du projet

```
Projet_POA_GACI-Louiza_BOUHADJAR-Abir_BACHI-Meriem_LAZREG-Aymene/
├── main.py          
├── recipes.py          
├── chef1.png          
├── chef2.png           
└── .idea/               
```

---

## Description du projet

### Principe
Une cuisine est représentée sur un canevas Tkinter : les ingrédients disponibles, un plan de travail et un comptoir de service. Un ou deux chefs se déplacent sur ce canevas pour :
1. **Ramasser** les ingrédients requis par la recette sélectionnée,
2. **Préparer** chaque ingrédient (les méthodes associées : rincer, couper, griller, etc.),
3. **Servir** le plat au comptoir.

### Recettes (`recipes.py`)
20 recettes sont définies (salades, sandwiches, plats de viande/poisson, omelettes...), chacune composée :
- d'une liste d'**ingrédients** requis,
- d'un dictionnaire de **méthodes** de préparation par ingrédient (ex. `"tomato": ["rinse", "slice"]`).

14 ingrédients de base sont disponibles : salade, tomate, oignon, carotte, poivron, poulet, bœuf, poisson, œuf, fromage, pain, concombre, citron, laitue.

### Agent cuisinier (`ChefAgent`)
Chaque chef est un agent autonome avec :
- `move_to` : déplacement fluide vers une position cible sur le canevas,
- `pick_ingredient` : ramassage d'un ingrédient (surlignage visuel),
- `perform_method` : exécution d'une étape de préparation,
- `serve` : dépôt du plat terminé au comptoir et mise à jour du score,
- `cooperate` : mode coopératif avancé avec répartition des ingrédients entre les deux chefs et synchronisation par threads/verrous (`threading.Lock`).

### Modes de jeu
| Mode                          | Description                                                                 |
|--------------------------------|---------------------------------------------------------------------------|
| **Solo** (`prepare_dish`)       | Un seul chef exécute toutes les étapes de la recette séquentiellement      |
| **Coopératif** (`cooperate`)    | Les ingrédients sont répartis (pairs/impairs) entre les 2 chefs qui travaillent en parallèle (threads), avec synchronisation avant le service |
| **Commande aléatoire**          | Génère une recette aléatoire à préparer                                    |
| **Test Solo 30s**               | Enchaîne automatiquement des recettes aléatoires en solo pendant 30 secondes et compte les plats terminés |
| **Test Coop 30s**               | Même principe en mode coopératif, pour comparer les performances solo vs coop |

### Interface (Tkinter)
- Canevas de jeu avec ingrédients, plan de travail, comptoir et sprites des chefs.
- Liste déroulante (`Combobox`) pour choisir une recette.
- Chronomètre (60s en jeu normal, 30s en mode test) et compteur de plats servis.
- Zone de log (`Text`) affichant en direct les actions de chaque chef.
- Boutons : *Préparer le plat (Chef 1)*, *Nouvelle commande aléatoire*, *Préparer ensemble*, *Test 30s (Solo)*, *Test 30s (Coop)*.

---

## Installation

Prérequis : **Python 3.12+** (Tkinter est inclus dans la distribution standard de Python sur la plupart des systèmes).

```bash
# Sous Linux, si Tkinter n'est pas déjà présent :
sudo apt-get install python3-tk
```


## Exécution

```bash
python main.py
```
