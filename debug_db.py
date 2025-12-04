import sys
import os

sys.path.append('src')

from database import DataBase


def debug_database():
    """Отладочная функция для проверки состояния базы данных"""
    db = DataBase()
    session = db.Session()

    try:
        # 1. Проверяем общее количество рецептов
        from database import Recipe, User, Category, Ingredient
        recipes = session.query(Recipe).all()
        print(f"=== ВСЕГО РЕЦЕПТОВ В БАЗЕ: {len(recipes)} ===")

        # 2. Выводим все рецепты с деталями
        for recipe in recipes:
            print(f"\nРецепт ID: {recipe.id}")
            print(f"Название: '{recipe.name}'")
            print(f"Пользователь ID: {recipe.user_id}")
            print(f"Изображение: {recipe.image}")
            print(f"Категории: {[cat.name for cat in recipe.categories]}")
            print(f"Типы категорий: {[cat.type for cat in recipe.categories]}")

            # Проверяем тип блюда
            dish_type = None
            cuisine = None
            for cat in recipe.categories:
                if cat.type == 'dish_type':
                    dish_type = cat.name
                elif cat.type == 'cuisine':
                    cuisine = cat.name
            print(f"Тип блюда: {dish_type}")
            print(f"Кухня: {cuisine}")

        # 3. Проверяем конкретный рецепт
        print("\n=== ПОИСК КОНКРЕТНОГО РЕЦЕПТА ===")
        target_names = ["Французский тост с бананово-карамельным соусом",
                        "французский тост",
                        "Французский тост"]

        for name in target_names:
            recipes = session.query(Recipe).filter(Recipe.name.ilike(f'%{name}%')).all()
            if recipes:
                print(f"Найдены рецепты по запросу '{name}':")
                for r in recipes:
                    print(f"  - ID: {r.id}, Название: '{r.name}', Изображение: {r.image}")
            else:
                print(f"Рецепты по запросу '{name}' не найдены")

        # 4. Проверяем пользователей
        users = session.query(User).all()
        print(f"\n=== ПОЛЬЗОВАТЕЛИ: {len(users)} ===")
        for user in users:
            print(f"ID: {user.id}, Логин: {user.login}")
            # Рецепты пользователя
            user_recipes = session.query(Recipe).filter_by(user_id=user.id).all()
            print(f"  Рецептов у пользователя: {len(user_recipes)}")
            for r in user_recipes:
                print(f"    - {r.id}: {r.name}")

        # 5. Проверяем категории
        categories = session.query(Category).all()
        print(f"\n=== КАТЕГОРИИ: {len(categories)} ===")
        for cat in categories:
            print(f"ID: {cat.id}, Название: '{cat.name}', Тип: '{cat.type}'")
            print(f"  Рецептов в категории: {len(cat.recipes)}")

        # 6. Проверяем назначение изображений
        recipes_without_images = session.query(Recipe).filter(Recipe.image.is_(None)).all()
        print(f"\n=== РЕЦЕПТОВ БЕЗ ИЗОБРАЖЕНИЙ: {len(recipes_without_images)} ===")
        for r in recipes_without_images:
            print(f"  - {r.id}: {r.name}")

        # 7. Проверяем таблицу рецепт_категории
        from sqlalchemy import text
        result = session.execute(text("SELECT * FROM Recipe_categories"))
        print(f"\n=== СВЯЗИ РЕЦЕПТ-КАТЕГОРИЯ ===")
        for row in result:
            print(f"  Рецепт ID: {row.recipe_id}, Категория ID: {row.category_id}")

    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    debug_database()