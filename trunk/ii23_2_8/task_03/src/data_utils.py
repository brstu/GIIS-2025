import csv

CSV_FILE = 'recipes.csv'
FIELDNAMES = ["id", "name", "ingredients", "difficulty", "steps", "image"]

def load_recipes():
    recipes = []
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['id'] = int(row['id'])
                row['ingredients'] = row['ingredients'].split(';')
                recipes.append(row)
    except FileNotFoundError:
        pass
    return recipes

def save_recipe(recipe):
    with open(CSV_FILE, mode='a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerow(recipe)

def get_next_id():
    recipes = load_recipes()
    return max((r['id'] for r in recipes), default=0) + 1
