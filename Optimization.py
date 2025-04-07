import functools

from NetworkGridModel import grid_model


def log_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(
            f"[ИМЯ ФУНКЦИИ] {func.__name__} [АРГУМЕНТ] = {args} [АРГУМЕНТЫ имен.] = {kwargs}")
        result = func(*args, **kwargs)
        print(f"[ВОЗРВАЩАЕТ] {func.__name__} -> {result}")
        return result
    return wrapper


@log_calls
def main():
    grid_model.set_load([0.6, 0.7, 0.5, 0.8, 0.05, 0.75, 0.8, 0.85, 0.0])

    grid_model.set_salary_cost(500_000)

    current_load = grid_model.get_load()
    salary_cost = grid_model.get_salary_cost()

    print("Current load factors:", current_load)
    print("Total salary cost:", salary_cost)

    # Здесь оптимизационная логика
    optimized_cost = salary_cost * 0.9  # Пример оптимизации
    print("Optimized cost:", optimized_cost)


main()
