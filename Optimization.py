from NetworkGridModel import grid_model


def set_load():
    new_load = [0.6, 0.7, 0.5, 0.8, 0.05, 0.75,
                0.8, 0.85, 0.0]  # Измененный массив
    grid_model.set_load(new_load)
    print("Updated load:", grid_model.get_load())
