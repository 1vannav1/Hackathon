from NetworkGridModel import grid_model


def main():
    grid_model.set_load([0.1, 0.2, 0.3, 0.4, 0.5])

    grid_model.set_salary_cost(500_000)

    current_load = grid_model.get_load()
    salary_cost = grid_model.get_salary_cost()

    print("Current load factors:", current_load)
    print("Total salary cost:", salary_cost)

    # Здесь оптимизационная логика
    optimized_cost = salary_cost * 0.9  # Пример оптимизации
    print("Optimized cost:", optimized_cost)
