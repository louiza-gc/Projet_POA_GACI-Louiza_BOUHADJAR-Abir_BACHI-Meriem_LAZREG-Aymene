import tkinter as tk
import time
import random
import threading
from recipes import recipes  # fichier recipes.py
from tkinter import ttk

available_ingredients = [
    "salad", "tomato", "onion", "carrot", "pepper",
    "chicken", "beef", "fish", "egg",
    "cheese", "bread", "cucumber", "lemon", "lettuce"
]

# Variables globales pour contrôler l'exécution des tests
test_mode = False
test_timer_running = False
test_start_time = 0
test_count = 0
stop_test_flag = False

# Variables pour la coopération
coop_total_steps = 0
coop_completed_steps = 0
coop_lock = threading.Lock()
all_ingredients_picked = False
coop_served = False

# ------------------ Fonctions pour la coopération ------------------
def compute_total_steps(recipe):
    """Calcule le nombre total d'étapes pour une recette"""
    total = 0
    for ingredient in recipe["ingredients"]:
        if ingredient in recipe["methods"]:
            total += len(recipe["methods"][ingredient])
    return total

def reset_coop_variables():
    """Réinitialise les variables de coopération"""
    global coop_total_steps, coop_completed_steps, all_ingredients_picked, coop_served
    coop_total_steps = 0
    coop_completed_steps = 0
    all_ingredients_picked = False
    coop_served = False

# ------------------ Fenêtre commande servie ------------------
def show_order_served():
    if not test_mode:  # Ne pas afficher en mode test
        served_window = tk.Toplevel()
        served_window.title("Commande servie !!")
        served_window.geometry("300x150")
        tk.Label(served_window, text="Commande servie !", font=("Arial", 24)).pack(expand=True)

# ------------------ Réinitialisation ------------------
def reset_ingredients_colors():
    for ing_shape in ingredients_shapes.values():
        canvas.itemconfig(ing_shape, fill="white")
    canvas.update()

# ------------------ Réinitialisation position chefs ------------------
def reset_chefs_position():
    """Réinitialise les chefs à leur position de départ"""
    canvas.coords(chef1_shape, 20, 350)
    canvas.coords(chef2_shape, 100, 350)
    canvas.update()

# ------------------ THREAD UTILITY ------------------
def run_in_thread(func):
    t = threading.Thread(target=func)
    t.daemon = True
    t.start()

# ------------------ Chef Agent ------------------
class ChefAgent:
    def __init__(self, canvas, chef_shape, output_widget, name="Chef"):
        self.canvas = canvas
        self.chef = chef_shape
        self.output = output_widget
        self.name = name
        self.x, self.y = self.canvas.coords(self.chef)[:2]

    def move_to(self, target_x, target_y, speed=5):
        while True:
            # Vérifier si le test doit s'arrêter
            if stop_test_flag:
                return
                
            coords = self.canvas.coords(self.chef)

            # Vérifier si c'est une image (2 valeurs) ou un rectangle (4 valeurs)
            if len(coords) == 2:
                cx, cy = coords
            else:
                cx = (coords[0] + coords[2]) / 2
                cy = (coords[1] + coords[3]) / 2

            dx = dy = 0
            if cx < target_x:
                dx = min(speed, target_x - cx)
            elif cx > target_x:
                dx = -min(speed, cx - target_x)
            if cy < target_y:
                dy = min(speed, target_y - cy)
            elif cy > target_y:
                dy = -min(speed, cy - target_y)

            if dx == 0 and dy == 0:
                break

            # Vérifier à nouveau avant de déplacer
            if stop_test_flag:
                return
                
            self.canvas.move(self.chef, dx, dy)
            self.canvas.update()
            time.sleep(0.01)

    def pick_ingredient(self, ingredient_shape, ing_name):
        if stop_test_flag:
            return
        self.output.insert(tk.END, f"{self.name} prend {ing_name}...\n")
        self.output.yview_moveto(1)
        canvas.itemconfig(ingredient_shape, fill="green")
        canvas.update()
        time.sleep(0.4)

    def perform_method(self, ing_name, method):
        if stop_test_flag:
            return
        self.output.insert(tk.END, f"{self.name} {method} {ing_name}...\n")
        self.output.yview_moveto(1)
        canvas.update()
        time.sleep(0.4)

    def serve(self, counter_shape):
        global start_time, score, timer_running

        if stop_test_flag:
            return

        end_time = time.time()
        elapsed = int(end_time - start_time)
        if not test_mode:
            timer_running = False
            timer_label.config(text=f"✔ Commande servie en {elapsed}s")

        global recipes_count
        recipes_count += 1
        score_label.config(text=f"Recettes servies : {recipes_count}")

        self.output.insert(tk.END, f"\n{self.name} a servi un plat !\n")
        self.output.yview_moveto(1)
        canvas.update()
        
        # Ne pas afficher la fenêtre en mode test
        if not test_mode:
            show_order_served()

    # ---------------- COOPÉRATION PARALLÈLE AMÉLIORÉE ------------------
    def cooperate(self, other_agent, dish_order, ingredients_shapes, prep_pos, counter_pos, counter_shape):
        global start_time, timer_running, all_ingredients_picked, coop_served

        self.output.delete("1.0", tk.END)

        if dish_order not in recipes:
            self.output.insert(tk.END, "Recette inconnue...\n")
            return

        reset_ingredients_colors()
        reset_coop_variables()
        start_timer()

        recipe = recipes[dish_order]
        required_ingredients = recipe["ingredients"]
        methods = recipe["methods"]

        # Calculer le total d'étapes
        coop_total_steps = compute_total_steps(recipe)
        self.output.insert(tk.END, f"🧑‍🍳 Mode COOP - Total des étapes : {coop_total_steps}\n")
        self.output.yview_moveto(1)

        # Répartir les ingrédients entre les chefs
        chef1_ingredients = [ing for i, ing in enumerate(required_ingredients) if i % 2 == 0]
        chef2_ingredients = [ing for i, ing in enumerate(required_ingredients) if i % 2 == 1]

        self.output.insert(tk.END, f"👨‍🍳 Chef 1 s'occupe de : {', '.join(chef1_ingredients)}\n")
        self.output.insert(tk.END, f"👩‍🍳 Chef 2 s'occupe de : {', '.join(chef2_ingredients)}\n")
        self.output.yview_moveto(1)

        # Compteur pour suivre les ingrédients ramassés
        picked_ingredients = set()
        pick_lock = threading.Lock()

        def ingredient_picked(ing_name):
            with pick_lock:
                picked_ingredients.add(ing_name)
                if len(picked_ingredients) == len(required_ingredients):
                    global all_ingredients_picked
                    all_ingredients_picked = True
                    self.output.insert(tk.END, "✅ Tous les ingrédients sont ramassés ! Début de la préparation...\n")
                    self.output.yview_moveto(1)

        def increment_step():
            global coop_completed_steps
            with coop_lock:
                coop_completed_steps += 1
                self.output.insert(tk.END, f"📊 Progression : {coop_completed_steps}/{coop_total_steps} étapes\n")
                self.output.yview_moveto(1)
                return coop_completed_steps

        def check_and_serve():
            global coop_served
            if stop_test_flag or coop_served:
                return False
                
            with coop_lock:
                if coop_completed_steps >= coop_total_steps and not coop_served:
                    coop_served = True
                    return True
            return False

        # ---------------- THREAD CHEF 1 ------------------
        def chef1_task():
            # Chef 1 prend SES ingrédients (pairs seulement)
            for ing in chef1_ingredients:
                if stop_test_flag:
                    return
                x1, y1, x2, y2 = canvas.coords(ingredients_shapes[ing])
                self.move_to(x1, y1)
                self.pick_ingredient(ingredients_shapes[ing], ing)
                ingredient_picked(ing)

            # Attendre que tous les ingrédients soient ramassés
            while not all_ingredients_picked and not stop_test_flag:
                time.sleep(0.1)

            # Préparer SES ingrédients seulement
            if not stop_test_flag:
                self.move_to(prep_pos[0], prep_pos[1])
                for ing in chef1_ingredients:
                    if ing in methods and not stop_test_flag:
                        for action in methods[ing]:
                            self.perform_method(ing, action)
                            increment_step()

            # Vérifier si on peut servir
            if check_and_serve():
                self.move_to(counter_pos[0], counter_pos[1])
                self.serve(counter_shape)
            else:
                # Retour à la position initiale
                self.move_to(20, 350)

        # ---------------- THREAD CHEF 2 ------------------
        def chef2_task():
            # Chef 2 prend SES ingrédients (impairs seulement)
            for ing in chef2_ingredients:
                if stop_test_flag:
                    return
                x1, y1, x2, y2 = canvas.coords(ingredients_shapes[ing])
                other_agent.move_to(x1, y1)
                other_agent.pick_ingredient(ingredients_shapes[ing], ing)
                ingredient_picked(ing)

            # Attendre que tous les ingrédients soient ramassés
            while not all_ingredients_picked and not stop_test_flag:
                time.sleep(0.1)

            # Préparer SES ingrédients seulement
            if not stop_test_flag:
                other_agent.move_to(prep_pos[0] + 50, prep_pos[1])
                for ing in chef2_ingredients:
                    if ing in methods and not stop_test_flag:
                        for action in methods[ing]:
                            other_agent.perform_method(ing, action)
                            increment_step()

            # Vérifier si on peut servir
            if check_and_serve():
                other_agent.move_to(counter_pos[0], counter_pos[1])
                other_agent.serve(counter_shape)
            else:
                # Retour à la position initiale
                other_agent.move_to(100, 350)

        # ---------------- LANCEMENT PARALLÈLE ------------------
        t1 = threading.Thread(target=chef1_task)
        t2 = threading.Thread(target=chef2_task)

        t1.start()
        t2.start()

        # Attendre la fin des deux threads
        def wait_for_completion():
            t1.join()
            t2.join()
            # Réinitialiser après completion
            reset_chefs_position()
            
        completion_thread = threading.Thread(target=wait_for_completion)
        completion_thread.daemon = True
        completion_thread.start()

# ------------------ Timer ------------------
def start_timer():
    global timer_running, start_time
    if timer_running:
        return
    timer_running = True
    start_time = time.time()
    update_timer()

def update_timer():
    global timer_running, start_time
    if not timer_running:
        return
    elapsed = int(time.time() - start_time)
    remaining = max(0, 60 - elapsed)
    timer_label.config(text=f"⏱ Temps restant : {remaining}s")
    if remaining > 0:
        root.after(1000, update_timer)
    else:
        timer_running = False
        timer_label.config(text="⛔ Temps écoulé !")

def start_test_timer():
    global test_timer_running, test_start_time
    test_timer_running = True
    test_start_time = time.time()
    update_test_timer()

def update_test_timer():
    global test_timer_running, test_start_time, stop_test_flag

    if not test_timer_running:
        return

    elapsed = int(time.time() - test_start_time)
    remaining = max(0, 30 - elapsed)

    timer_label.config(text=f"⏱ Test : {remaining}s")

    if remaining > 0:
        root.after(1000, update_test_timer)
    else:
        # Temps écoulé - arrêter le test
        test_timer_running = False
        stop_test_flag = True
        timer_label.config(text="⏱ Test terminé !")
        
        # Réinitialiser les positions des chefs
        reset_chefs_position()
        
        # Réinitialiser le flag après un court délai
        root.after(100, lambda: setattr(globals(), 'stop_test_flag', False))

# ------------------ Commande aléatoire ------------------
recipes_count = 0
timer_running = False
start_time = 0

def generate_random_order():
    return random.choice(list(recipes.keys()))

def start_test_solo_30s():
    global test_mode, test_count, test_end_time, test_timer_running, stop_test_flag

    if timer_running or test_timer_running:
        return

    # Réinitialiser le flag d'arrêt
    stop_test_flag = False
    
    test_mode = True
    test_count = 0
    test_end_time = time.time() + 30

    # Affiche 30s immédiatement
    timer_label.config(text="⏱ Test : 30s")

    start_test_timer()

    output.insert(tk.END, "=== TEST SOLO 30s : DÉBUT ===\n")

    def loop():
        global test_count, test_mode
        while time.time() < test_end_time and not stop_test_flag:
            order = generate_random_order()

            # ➤ Affichage dans le champ texte
            def update_ui(o=order):
                entry.delete(0, tk.END)
                entry.insert(0, o)
                output.insert(tk.END, f"\nTest : recette {o.upper()}\n")
                output.yview_moveto(1)
            
            root.after(0, update_ui)

            # Préparer le plat si le test n'est pas arrêté
            if not stop_test_flag:
                prepare_dish(order, chef1, ingredients_shapes, output, (prep_x1, prep_y1), (counter_x1, counter_y1), counter)
                test_count += 1

        # Fin du test
        def finish_ui():
            global test_mode
            test_mode = False
            output.insert(tk.END, f"\n=== FIN TEST SOLO : {test_count} plats préparés ===\n")
            output.yview_moveto(1)
        
        if not stop_test_flag:  # Only show completion message if test wasn't stopped
            root.after(0, finish_ui)

    run_in_thread(loop)

def start_test_coop_30s():
    global test_mode, test_timer_running, stop_test_flag

    if timer_running or test_timer_running:
        return

    # Réinitialiser le flag d'arrêt
    stop_test_flag = False
    
    test_mode = True
    timer_label.config(text="⏱ Test : 30s")
    start_test_timer()

    output.insert(tk.END, "=== TEST COOP 30s : DÉBUT ===\n")
    output.yview_moveto(1)

    def test_worker():
        end_time = time.time() + 30
        completed = 0

        while time.time() < end_time and not stop_test_flag:
            # Réinitialiser les variables pour chaque plat
            reset_coop_variables()
            
            order = generate_random_order()
            recipe = recipes.get(order)
            if not recipe:
                continue

            required_ingredients = recipe["ingredients"]
            methods = recipe["methods"]
            
            # Calculer le total d'étapes
            coop_total_steps = compute_total_steps(recipe)

            # Répartir les ingrédients entre les chefs
            chef1_ingredients = [ing for i, ing in enumerate(required_ingredients) if i % 2 == 0]
            chef2_ingredients = [ing for i, ing in enumerate(required_ingredients) if i % 2 == 1]

            def ui_update(o=order):
                entry.delete(0, tk.END)
                entry.insert(0, o)
                output.insert(tk.END, f"\nTest : recette {o.upper()} (coop) - {coop_total_steps} étapes\n")
                output.insert(tk.END, f"👨‍🍳 Chef 1 s'occupe de : {', '.join(chef1_ingredients)}\n")
                output.insert(tk.END, f"👩‍🍳 Chef 2 s'occupe de : {', '.join(chef2_ingredients)}\n")
                output.yview_moveto(1)
            root.after(0, ui_update)

            # Variables locales pour ce plat
            plat_all_ingredients_picked = False
            plat_coop_completed_steps = 0
            plat_coop_served = False
            plat_picked_ingredients = set()
            plat_lock = threading.Lock()

            def plat_ingredient_picked(ing_name):
                nonlocal plat_all_ingredients_picked
                with plat_lock:
                    plat_picked_ingredients.add(ing_name)
                    if len(plat_picked_ingredients) == len(required_ingredients):
                        plat_all_ingredients_picked = True
                        output.insert(tk.END, "✅ Tous les ingrédients sont ramassés ! Début de la préparation...\n")
                        output.yview_moveto(1)

            def plat_increment_step():
                nonlocal plat_coop_completed_steps
                with plat_lock:
                    plat_coop_completed_steps += 1
                    output.insert(tk.END, f"📊 Progression : {plat_coop_completed_steps}/{coop_total_steps} étapes\n")
                    output.yview_moveto(1)
                    return plat_coop_completed_steps

            def plat_check_and_serve():
                nonlocal plat_coop_served
                if stop_test_flag or plat_coop_served:
                    return False
                    
                with plat_lock:
                    if plat_coop_completed_steps >= coop_total_steps and not plat_coop_served:
                        plat_coop_served = True
                        return True
                return False

            # --- définir les tâches des deux chefs ---
            def chef1_task():
                # Chef 1 prend SES ingrédients (pairs seulement)
                for ing in chef1_ingredients:
                    if stop_test_flag:
                        return
                    x1, y1, x2, y2 = canvas.coords(ingredients_shapes[ing])
                    chef1.move_to(x1, y1)
                    chef1.pick_ingredient(ingredients_shapes[ing], ing)
                    plat_ingredient_picked(ing)

                # Attendre que tous les ingrédients soient ramassés
                while not plat_all_ingredients_picked and not stop_test_flag:
                    time.sleep(0.1)

                # Préparer SES ingrédients seulement
                if not stop_test_flag:
                    chef1.move_to(prep_x1, prep_y1)
                    for ing in chef1_ingredients:
                        if ing in methods and not stop_test_flag:
                            for action in methods[ing]:
                                chef1.perform_method(ing, action)
                                plat_increment_step()

                # Vérifier si on peut servir
                if plat_check_and_serve():
                    chef1.move_to(counter_x1, counter_y1)
                    chef1.serve(counter)
                else:
                    # Retour à la position initiale
                    chef1.move_to(20, 350)

            def chef2_task():
                # Chef 2 prend SES ingrédients (impairs seulement)
                for ing in chef2_ingredients:
                    if stop_test_flag:
                        return
                    x1, y1, x2, y2 = canvas.coords(ingredients_shapes[ing])
                    chef2.move_to(x1, y1)
                    chef2.pick_ingredient(ingredients_shapes[ing], ing)
                    plat_ingredient_picked(ing)

                # Attendre que tous les ingrédients soient ramassés
                while not plat_all_ingredients_picked and not stop_test_flag:
                    time.sleep(0.1)

                # Préparer SES ingrédients seulement
                if not stop_test_flag:
                    chef2.move_to(prep_x1 + 50, prep_y1)
                    for ing in chef2_ingredients:
                        if ing in methods and not stop_test_flag:
                            for action in methods[ing]:
                                chef2.perform_method(ing, action)
                                plat_increment_step()

                # Vérifier si on peut servir
                if plat_check_and_serve():
                    chef2.move_to(counter_x1, counter_y1)
                    chef2.serve(counter)
                else:
                    # Retour à la position initiale
                    chef2.move_to(100, 350)

            # lancer les deux threads pour la coopération
            t1 = threading.Thread(target=chef1_task)
            t2 = threading.Thread(target=chef2_task)
            t1.start()
            t2.start()

            # attendre la fin des deux chefs
            t1.join()
            t2.join()

            if not stop_test_flag and plat_coop_served:
                completed += 1

            # Réinitialiser les couleurs et positions pour le prochain plat
            reset_ingredients_colors()
            reset_chefs_position()
            time.sleep(0.1)

        # Fin du test
        def finish_ui():
            global test_mode
            test_mode = False
            output.insert(tk.END, f"\n=== FIN TEST COOP : {completed} plats préparés ===\n")
            output.yview_moveto(1)
        root.after(0, finish_ui)

    run_in_thread(test_worker)

def start_order():
    if timer_running:
        return
    reset_ingredients_colors()
    order = generate_random_order()
    entry.delete(0, tk.END)
    entry.insert(0, order)
    output.insert(tk.END, f"Nouvelle commande : {order.upper()} !\n")
    output.yview_moveto(1)
    prepare_dish(order, chef1, ingredients_shapes, output, (prep_x1, prep_y1), (counter_x1, counter_y1), counter)

# ------------------ VERSION CHEF SEUL ------------------
def prepare_dish(dish_order, chef_agent, ingredients_shapes, output_widget, prep_pos, counter_pos, counter_shape):
    global timer_running, start_time
    output_widget.delete("1.0", tk.END)

    if dish_order not in recipes:
        output_widget.insert(tk.END, "Recette inconnue.\n")
        return

    reset_ingredients_colors()
    if not test_mode:
        start_timer()

    recipe = recipes[dish_order]
    required_ingredients = recipe["ingredients"]
    methods = recipe["methods"]

    for ing in required_ingredients:
        if stop_test_flag:  # Vérifier à chaque ingrédient
            return
        x1, y1, x2, y2 = canvas.coords(ingredients_shapes[ing])
        chef_agent.move_to(x1, y1)
        chef_agent.pick_ingredient(ingredients_shapes[ing], ing)

    if stop_test_flag:  # Vérifier avant la préparation
        return
        
    chef_agent.move_to(prep_pos[0], prep_pos[1])

    for ing in required_ingredients:
        if ing in methods and not stop_test_flag:
            for action in methods[ing]:
                chef_agent.perform_method(ing, action)

    if stop_test_flag:  # Vérifier avant de servir
        return
        
    chef_agent.move_to(counter_pos[0], counter_pos[1])
    chef_agent.serve(counter_shape)

def reset_plats_prepared():
    global recipes_count
    recipes_count = 0
    score_label.config(text=f"Recettes servies : {recipes_count}")

# ------------------ GUI TKINTER ------------------
root = tk.Tk()
root.title("Overcooked Multijoueur Coop")
root.geometry("1250x700")
root.resizable(False, False)

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

main_canvas = tk.Canvas(main_frame)
main_canvas.pack(side="left", fill="both", expand=True)

# === PANEL À DROITE POUR LES BOUTONS ===
buttons_frame = tk.Frame(main_frame, padx=10, pady=10, bg="lightgrey")
buttons_frame.pack(side="right", fill="y")

content_frame = tk.Frame(main_canvas)
main_canvas.create_window((0, 0), window=content_frame, anchor="nw")

title_label = tk.Label(content_frame, text="Overcooked Multijoueur Coop 🧑‍🍳👩‍🍳", font=("Arial", 24, "bold"))
title_label.pack(pady=10)

# Liste des plats depuis recipes
dish_names = list(recipes.keys())

# Drop-list pour sélectionner un plat
entry = ttk.Combobox(
    buttons_frame,
    values=dish_names,
    font=("Arial", 14),
    state="readonly"
)
entry.pack(pady=5, fill="x")

# Optionnel : sélectionne le 1er plat par défaut
entry.set(dish_names[0])

timer_label = tk.Label(content_frame, text="⏱ Temps restant : 60s", font=("Arial", 14, "bold"), fg="red")
timer_label.pack(pady=5)

score_label = tk.Label(content_frame, text="Recettes servies : 0", font=("Arial", 14, "bold"), fg="green")
score_label.pack(pady=5)

output = tk.Text(buttons_frame, height=15, width=40, font=("Arial", 12))
output.pack(pady=10)

canvas = tk.Canvas(content_frame, width=850, height=400, bg="lightblue")
canvas.pack(pady=10)

# Charger les images
chef1_img = tk.PhotoImage(file="chef1.png")
chef2_img = tk.PhotoImage(file="chef2.png")  # nouvelle image pour chef2

# Créer les images sur le canvas
chef1_shape = canvas.create_image(20, 350, image=chef1_img, anchor="nw")
chef2_shape = canvas.create_image(100, 350, image=chef2_img, anchor="nw")

# Garder une référence aux images pour éviter le garbage collector
canvas.chef1_img = chef1_img
canvas.chef2_img = chef2_img

# Créer les agents
chef1 = ChefAgent(canvas, chef1_shape, output, name="Chef 1")
chef2 = ChefAgent(canvas, chef2_shape, output, name="Chef 2")

# Ingredients
ingredients_shapes = {}
rows = 2
cols = (len(available_ingredients) + 1) // 2
spacing_x = 100
spacing_y = 100
start_x = 50
start_y = 50

for i, ing in enumerate(available_ingredients):
    row = i // cols
    col = i % cols
    x1 = start_x + col * spacing_x
    y1 = start_y + row * spacing_y
    x2 = x1 + 40
    y2 = y1 + 40
    ingredients_shapes[ing] = canvas.create_rectangle(x1, y1, x2, y2, fill="white")
    canvas.create_text((x1 + x2)//2, y1 - 10, text=ing, font=("Arial", 10))

# Zones
prep_x1, prep_y1, prep_x2, prep_y2 = 350, 350, 500, 390
prep_area = canvas.create_rectangle(prep_x1, prep_y1, prep_x2, prep_y2, fill="grey")
canvas.create_text((prep_x1 + prep_x2)//2, prep_y1 - 10, text="Plan de travail", font=("Arial", 12))

counter_x1, counter_y1, counter_x2, counter_y2 = 750, 50, 800, 150
counter = canvas.create_rectangle(counter_x1, counter_y1, counter_x2, counter_y2, fill="white")
canvas.create_text((counter_x1 + counter_x2)//2, counter_y1 - 10, text="Comptoir", font=("Arial", 12))

# Buttons
tk.Button(
    buttons_frame,
    text="Préparer le plat (Chef 1)",
    font=("Arial", 14),
    command=lambda: run_in_thread(
        lambda: prepare_dish(
            entry.get().strip().lower(),
            chef1,
            ingredients_shapes,
            output,
            (prep_x1, prep_y1),
            (counter_x1, counter_y1),
            counter
        )
    )
).pack(pady=5)

tk.Button(
    buttons_frame,
    text="Nouvelle commande aléatoire 🍽️",
    font=("Arial", 14),
    command=start_order
).pack(pady=5)

tk.Button(
    buttons_frame,
    text="Préparer ensemble (Chef 1 + Chef 2)",
    font=("Arial", 14),
    command=lambda: run_in_thread(
        lambda: chef1.cooperate(
            chef2,
            entry.get().strip().lower(),
            ingredients_shapes,
            (prep_x1, prep_y1),
            (counter_x1, counter_y1),
            counter
        )
    )
).pack(pady=5)

tk.Button(
    buttons_frame,
    text="Test 30s (Solo) 🚀",
    font=("Arial", 14),
    command=lambda: (
        reset_plats_prepared(),
        start_test_solo_30s()
    )
).pack(pady=5)

tk.Button(
    buttons_frame,
    text="Test 30s (Coop) 🤝",
    font=("Arial", 14),
    command=lambda: (
        reset_plats_prepared(),
        start_test_coop_30s()
    )
).pack(pady=5)

root.mainloop()