import tkinter as tk
import time
import random
import threading
from recipes import recipes  # fichier recipes.py

available_ingredients = [
    "salad", "tomato", "onion", "carrot", "pepper",
    "chicken", "beef", "fish", "egg",
    "cheese", "bread", "cucumber", "lemon", "lettuce"
]



# ------------------ Fenêtre commande servie ------------------
def show_order_served():
    served_window = tk.Toplevel()
    served_window.title("Commande servie !")
    served_window.geometry("300x150")
    tk.Label(served_window, text="Commande servie !", font=("Arial", 24)).pack(expand=True)

# ------------------ Réinitialisation ------------------
def reset_ingredients_colors():
    for ing_shape in ingredients_shapes.values():
        canvas.itemconfig(ing_shape, fill="white")
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
            cx1, cy1, cx2, cy2 = self.canvas.coords(self.chef)
            dx = dy = 0
            if cx1 < target_x:
                dx = min(speed, target_x - cx1)
            elif cx1 > target_x:
                dx = -min(speed, cx1 - target_x)
            if cy1 < target_y:
                dy = min(speed, target_y - cy1)
            elif cy1 > target_y:
                dy = -min(speed, cy1 - target_y)
            if dx == 0 and dy == 0:
                break
            self.canvas.move(self.chef, dx, dy)
            self.canvas.update()
            time.sleep(0.01)

    def pick_ingredient(self, ingredient_shape, ing_name):
        self.output.insert(tk.END, f"{self.name} prend {ing_name}...\n")
        self.output.yview_moveto(1)
        canvas.itemconfig(ingredient_shape, fill="green")
        canvas.update()
        time.sleep(0.4)

    def perform_method(self, ing_name, method):
        self.output.insert(tk.END, f"{self.name} {method} {ing_name}...\n")
        self.output.yview_moveto(1)
        canvas.update()
        time.sleep(0.4)

    def serve(self, counter_shape):
        global start_time, score, timer_running

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


    # ---------------- COOPÉRATION PARALLÈLE ------------------
    def cooperate(self, other_agent, dish_order, ingredients_shapes, prep_pos, counter_pos, counter_shape):
        global start_time, timer_running

        self.output.delete("1.0", tk.END)

        if dish_order not in recipes:
            self.output.insert(tk.END, "Recette inconnue...\n")
            return

        reset_ingredients_colors()
        start_timer()

        recipe = recipes[dish_order]
        required_ingredients = recipe["ingredients"]
        methods = recipe["methods"]

        # ---------------- THREAD CHEF 1 ------------------
        def chef1_task():
            for i, ing in enumerate(required_ingredients):
                if i % 2 == 0:
                    x1, y1, x2, y2 = canvas.coords(ingredients_shapes[ing])
                    self.move_to(x1, y1)
                    self.pick_ingredient(ingredients_shapes[ing], ing)

            self.move_to(prep_pos[0], prep_pos[1])
            for ing in required_ingredients:
                if ing in methods:
                    for action in methods[ing]:
                        self.perform_method(ing, action)

        # ---------------- THREAD CHEF 2 ------------------
        def chef2_task():
            for i, ing in enumerate(required_ingredients):
                if i % 2 == 1:
                    x1, y1, x2, y2 = canvas.coords(ingredients_shapes[ing])
                    other_agent.move_to(x1, y1)
                    other_agent.pick_ingredient(ingredients_shapes[ing], ing)

            other_agent.move_to(prep_pos[0] + 50, prep_pos[1])
            time.sleep(1)

            other_agent.move_to(counter_pos[0], counter_pos[1])
            other_agent.serve(counter_shape)

        # ---------------- LANCEMENT PARALLÈLE ------------------
        t1 = threading.Thread(target=chef1_task)
        t2 = threading.Thread(target=chef2_task)

        t1.start()
        t2.start()

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
    global test_timer_running, test_start_time

    if not test_timer_running:
        return

    elapsed = int(time.time() - test_start_time)
    remaining = max(0, 30 - elapsed)

    timer_label.config(text=f"⏱ Test : {remaining}s")

    if remaining > 0:
        root.after(1000, update_test_timer)
    else:
        test_timer_running = False
        timer_label.config(text="⏱ Test terminé !")

# ------------------ Commande aléatoire ------------------
recipes_count = 0
timer_running = False
start_time = 0

test_mode = False
test_count = 0
test_end_time = 0

test_timer_running = False
test_start_time = 0


def start_test_solo_30s():
    global test_mode, test_count, test_end_time, test_timer_running

    if timer_running or test_timer_running:
        return

    test_mode = True
    test_count = 0
    test_end_time = time.time() + 30

    # Affiche 30s immédiatement
    timer_label.config(text="⏱ Test : 30s")

    start_test_timer()

    output.insert(tk.END, "=== TEST SOLO 30s : DÉBUT ===\n")

    def loop():
        global test_count, test_mode
        while time.time() < test_end_time:
            order = generate_random_order()

            # ➤ Affichage dans le champ texte
            entry.delete(0, tk.END)
            entry.insert(0, order)

            output.insert(tk.END, f"\nTest : recette {order.upper()}\n")
            prepare_dish(order, chef1, ingredients_shapes, output, (prep_x1, prep_y1), (counter_x1, counter_y1), counter)
            test_count += 1

        test_mode = False
        output.insert(tk.END, f"\n=== FIN TEST SOLO : {test_count} plats préparés ===\n")

    run_in_thread(loop)


def start_test_coop_30s():
    global test_mode, test_count, test_end_time, test_timer_running

    if timer_running or test_timer_running:
        return

    test_mode = True
    test_count = 0
    test_end_time = time.time() + 30

    start_test_timer()

    output.insert(tk.END, "=== TEST SOLO 30s : DÉBUT ===\n")

    def loop():
        global test_count, test_mode
        while time.time() < test_end_time:
            order = generate_random_order()

            # ➤ Affichage dans l'input
            entry.delete(0, tk.END)
            entry.insert(0, order)

            output.insert(tk.END, f"\nTest : recette {order.upper()} (coop)\n")
            chef1.cooperate(chef2, order, ingredients_shapes, (prep_x1, prep_y1), (counter_x1, counter_y1), counter)
            test_count += 1

        test_mode = False
        output.insert(tk.END, f"\n=== FIN TEST COOP : {test_count} plats préparés ===\n")

    run_in_thread(loop)


def generate_random_order():
    return random.choice(list(recipes.keys()))

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
        x1, y1, x2, y2 = canvas.coords(ingredients_shapes[ing])
        chef_agent.move_to(x1, y1)
        chef_agent.pick_ingredient(ingredients_shapes[ing], ing)

    chef_agent.move_to(prep_pos[0], prep_pos[1])

    for ing in required_ingredients:
        if ing in methods:
            for action in methods[ing]:
                chef_agent.perform_method(ing, action)

    chef_agent.move_to(counter_pos[0], counter_pos[1])
    chef_agent.serve(counter_shape)


# ------------------ GUI TKINTER ------------------
root = tk.Tk()
root.title("Overcooked Multijoueur Coop")
root.geometry("900x700")

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

main_canvas = tk.Canvas(main_frame)
main_canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=main_canvas.yview)
scrollbar.pack(side="right", fill="y")

main_canvas.configure(yscrollcommand=scrollbar.set)
main_canvas.bind('<Configure>', lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))

content_frame = tk.Frame(main_canvas)
main_canvas.create_window((0, 0), window=content_frame, anchor="nw")

title_label = tk.Label(content_frame, text="Overcooked Multijoueur Coop 🧑‍🍳👩‍🍳", font=("Arial", 24, "bold"))
title_label.pack(pady=10)

entry = tk.Entry(content_frame, font=("Arial", 14))
entry.pack(pady=5)


timer_label = tk.Label(content_frame, text="⏱ Temps restant : 60s", font=("Arial", 14, "bold"), fg="red")
timer_label.pack(pady=5)

score_label = tk.Label(content_frame, text="Recettes servies : 0", font=("Arial", 14, "bold"), fg="green")
score_label.pack(pady=5)

output = tk.Text(content_frame, height=15, width=60, font=("Arial", 12))
output.pack(pady=10)

canvas = tk.Canvas(content_frame, width=850, height=400, bg="lightblue")
canvas.pack(pady=10)

# Chefs
chef1_shape = canvas.create_rectangle(20, 350, 60, 390, fill="red")
chef1 = ChefAgent(canvas, chef1_shape, output, name="Chef 1")

chef2_shape = canvas.create_rectangle(100, 350, 140, 390, fill="blue")
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
    content_frame,
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
    content_frame,
    text="Nouvelle commande aléatoire 🍽️",
    font=("Arial", 14),
    command=start_order
).pack(pady=5)

tk.Button(
    content_frame,
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
    content_frame,
    text="Test 30s (Solo) 🚀",
    font=("Arial", 14),
    command=start_test_solo_30s
).pack(pady=5)

tk.Button(
    content_frame,
    text="Test 30s (Coop) 🤝",
    font=("Arial", 14),
    command=start_test_coop_30s
).pack(pady=5)


root.mainloop()
