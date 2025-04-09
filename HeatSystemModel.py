import datetime


class HeatingObject:
    def __init__(
        self,
        name,
        installed_power_electric,
        heating_load,
        distance,
        load_factor_summer,
        load_factor_winter,
    ):
        self.name = name
        self.installed_power_electric = installed_power_electric
        self.heating_load = heating_load
        self.distance = distance
        self.load_factor_summer = load_factor_summer
        self.load_factor_winter = load_factor_winter
        self.total_fuel_consumption = 0  # Суммарное потребление топлива объектом
        self.total_heat_loss = 0  # Суммарные теплопотери объекта

    def calculate_heat_demand(self, temperature, heating_period):
        design_temperature = (
            ClimateData.design_temperature_heating
        )  # Расчетная температура для отопления

        if heating_period:
            # Если отопительный период, то считаем зависимость от температуры
            heat_demand = self.heating_load * max(
                0,
                (design_temperature - temperature)
                / (design_temperature - ClimateData.average_temperature_heating_period),
            )
        else:
            # Вне отопительного периода потребление минимально (мб и ноль принять надо, хз)
            heat_demand = self.heating_load * 0.1

        return heat_demand

    def __repr__(self):
        return f"{self.name} (Мощность: {self.installed_power_electric} МВт, Тепло: {self.heating_load} Гкал/ч, Затраты топлива: {self.total_fuel_consumption:.2f} м3, Потери тепла: {self.total_heat_loss:.2f} Гкал)"


class ProductionFacility(HeatingObject):
    pass


class LivingComplex(HeatingObject):
    pass


class WellCluster(HeatingObject):
    def __init__(
        self,
        name,
        installed_power_electric,
        distance,
        load_factor_summer,
        load_factor_winter,
    ):
        super().__init__(
            name,
            installed_power_electric,
            0,
            distance,
            load_factor_summer,
            load_factor_winter,
        )


class BoilerPlant:
    def __init__(self, name, fuel_type, fuel_heat_value, efficiency=0.9):
        self.name = name
        self.fuel_type = fuel_type
        self.fuel_heat_value = fuel_heat_value
        self.efficiency = efficiency
        self.supply_temperature = 95  # Температура в подающей магистрали (°C)
        self.return_temperature = 70  # Температура в обратной магистрали (°C)

    def calculate_fuel_consumption(self, heat_demand):
        """
        Рассчитывает потребление топлива для заданной тепловой нагрузки.
        """

        fuel_consumption = (heat_demand * 4186.8) / (
            self.fuel_heat_value * self.efficiency
        )
        return fuel_consumption

    def __repr__(self):
        return f"{self.name} (Топливо: {self.fuel_type}, Теплопроводность: {self.fuel_heat_value} кДж/м3, Поступающая температура: {self.supply_temperature}°C, Возвратная температура: {self.return_temperature}°C)"


class HeatingNetwork:
    def __init__(
        self,
        length,
        pipe_diameter=0.45,
        insulation_thickness=0.375,
        thermal_conductivity=0.03,
    ):
        self.length = length
        self.pipe_diameter = pipe_diameter  # Диаметр трубы (м)
        self.insulation_thickness = insulation_thickness  # Толщина изоляции (м)
        self.thermal_conductivity = (
            thermal_conductivity  # Теплопроводность изоляции (Вт/м*К)
        )
        self.total_heat_loss = 0

    def calculate_heat_loss(
        self, temperature, heat_load, supply_temperature, return_temperature
    ):
        # Средняя температура теплоносителя
        average_temperature = (supply_temperature + return_temperature) / 2

        # Разница температур между теплоносителем и окружающей средой
        temperature_difference = average_temperature - temperature

        # Упрощенный расчет тепловых потерь, учитывающий тепловую нагрузку
        total_heat_loss = 0.05 * temperature_difference * self.length * heat_load

        return total_heat_loss

    def __repr__(self):
        return f"Heating Network (Длина: {self.length} км, Диаметр: {self.pipe_diameter} м, Толщина изоляции: {self.insulation_thickness} м, Теплопроводность изоляции: {self.thermal_conductivity} Вт/м*К, Суммарные теплопотери: {self.total_heat_loss:.2f} Гкал)"  # Выводим теплопотери


class ClimateData:
    absolute_min_temperature = -54
    absolute_max_temperature = 34
    design_temperature_heating = -48
    design_temperature_ventilation = -36
    average_temperature_coldest_month = -26.5
    average_temperature_heating_period = -13.1
    average_max_temperature = 24.8
    heating_period_duration = 283
    heating_start_month = 9
    heating_start_day = 5

    # Средние температуры по месяца
    average_temperatures = {
        1: -25,  # Январь
        2: -23,  # Февраль
        3: -15,  # Март
        4: -3,  # Апрель
        5: 8,  # Май
        6: 18,  # Июнь
        7: 25,  # Июль
        8: 20,  # Август
        9: 12,  # Сентябрь
        10: 0,  # Октябрь
        11: -12,  # Ноябрь
        12: -20,  # Декабрь
    }


class HeatModel:
    def __init__(self, objects, boiler_plants, fuel_cost=1200):
        self.objects = objects
        self.boiler_plants = boiler_plants
        self.fuel_cost = fuel_cost  # руб/м3

        self.total_fuel_consumption = 0
        self.total_heat_loss = 0
        self.total_cost = 0
        self.temperature_data = {}

    def generate_temperature_data(self, start_date, end_date):
        current_date = start_date
        while current_date <= end_date:
            month = current_date.month
            temperature = ClimateData.average_temperatures.get(month)
            if temperature is not None:
                self.temperature_data[current_date.strftime("%Y-%m-%d")] = temperature
            else:
                self.temperature_data[current_date.strftime("%Y-%m-%d")] = (
                    ClimateData.average_temperature_heating_period
                )
            current_date += datetime.timedelta(days=1)

    def is_heating_period(self, date):
        "Определяет, является ли текущая дата частью отопительного периода"
        start_date = datetime.date(
            date.year, ClimateData.heating_start_month, ClimateData.heating_start_day
        )
        end_date = start_date + datetime.timedelta(
            days=ClimateData.heating_period_duration
        )

        if start_date <= end_date:
            return start_date <= date.date() <= end_date
        else:
            return date.date() >= start_date or date.date() <= end_date

    def simulate(self, start_date, end_date):

        self.generate_temperature_data(start_date, end_date)

        current_date = start_date
        networks = [
            HeatingNetwork(
                obj.distance,
                pipe_diameter=0.45,
                insulation_thickness=0.375,
                thermal_conductivity=0.03,
            )
            for obj in self.objects
        ]
        while current_date <= end_date:

            temperature = self.temperature_data[current_date.strftime("%Y-%m-%d")]

            heating_period = self.is_heating_period(current_date)
            # Рассчитываем потребление и потери для каждого объекта
            for obj, plant, network in zip(self.objects, self.boiler_plants, networks):
                heat_demand = obj.calculate_heat_demand(temperature, heating_period)
                fuel_consumption = plant.calculate_fuel_consumption(heat_demand)
                # Передаем температуры теплоносителя
                heat_loss = network.calculate_heat_loss(
                    temperature,
                    heat_demand,
                    plant.supply_temperature,
                    plant.return_temperature,
                )

                obj.total_fuel_consumption += fuel_consumption
                obj.total_heat_loss += heat_loss

                self.total_fuel_consumption += fuel_consumption
                self.total_heat_loss += heat_loss
                self.total_cost += fuel_consumption * self.fuel_cost

                network.total_heat_loss += heat_loss

            current_date += datetime.timedelta(days=1)

        print("---Результаты моделирования---")
        print(f"Общий расход топлива: {self.total_fuel_consumption:.2f} м3")
        print(f"Общие теплопотери: {self.total_heat_loss:.2f} Гкал")
        print(f"Общие затраты на топливо: {self.total_cost:.2f} руб.")

        print("\n---Состояние объектов---")
        for obj in self.objects:
            print(obj)

        print("\n---Состояние сетей---")
        for network in networks:
            print(network)


objects_data = [
    {
        "name": "УКПГ",
        "installed_power_electric": 30.0,
        "heating_load": 3.04,
        "distance": 0.50,
        "load_factor_summer": 90,
        "load_factor_winter": 95,
        "type": ProductionFacility,
    },
    {
        "name": "ОБП",
        "installed_power_electric": 9.0,
        "heating_load": 0.64,
        "distance": 3.0,
        "load_factor_summer": 80,
        "load_factor_winter": 90,
        "type": ProductionFacility,
    },
    {
        "name": "ВЖК",
        "installed_power_electric": 2.0,
        "heating_load": 0.35,
        "distance": 3.50,
        "load_factor_summer": 100,
        "load_factor_winter": 100,
        "type": LivingComplex,
    },
    {
        "name": "ПЖК",
        "installed_power_electric": 3.0,
        "heating_load": 2.58,
        "distance": 4.0,
        "load_factor_summer": 100,
        "load_factor_winter": 100,
        "type": LivingComplex,
    },
    {
        "name": "ПСП",
        "installed_power_electric": 10.0,
        "heating_load": 1.91,
        "distance": 100.0,
        "load_factor_summer": 100,
        "load_factor_winter": 100,
        "type": ProductionFacility,
    },
]

well_clusters_data = [
    {
        "name": "Куст 1",
        "installed_power_electric": 0.7,
        "distance": 1.0,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 2",
        "installed_power_electric": 0.8,
        "distance": 2.0,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 3",
        "installed_power_electric": 0.5,
        "distance": 3.0,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 4",
        "installed_power_electric": 0.9,
        "distance": 3.3,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 5",
        "installed_power_electric": 1.0,
        "distance": 4.0,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 6",
        "installed_power_electric": 0.9,
        "distance": 4.5,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 7",
        "installed_power_electric": 0.5,
        "distance": 5.0,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 8",
        "installed_power_electric": 1.0,
        "distance": 5.2,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 9",
        "installed_power_electric": 1.3,
        "distance": 5.7,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 10",
        "installed_power_electric": 1.0,
        "distance": 6.0,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 11",
        "installed_power_electric": 0.8,
        "distance": 6.5,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 12",
        "installed_power_electric": 0.6,
        "distance": 7.0,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 13",
        "installed_power_electric": 0.8,
        "distance": 7.5,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 14",
        "installed_power_electric": 1.0,
        "distance": 7.8,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 15",
        "installed_power_electric": 1.0,
        "distance": 8.0,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 16",
        "installed_power_electric": 0.7,
        "distance": 8.5,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 17",
        "installed_power_electric": 1.0,
        "distance": 9.0,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 18",
        "installed_power_electric": 0.8,
        "distance": 9.3,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 19",
        "installed_power_electric": 1.0,
        "distance": 9.7,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 20",
        "installed_power_electric": 1.1,
        "distance": 17.0,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 21",
        "installed_power_electric": 1.0,
        "distance": 18.0,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 22",
        "installed_power_electric": 2.2,
        "distance": 20.0,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 23",
        "installed_power_electric": 1.4,
        "distance": 22.0,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 24",
        "installed_power_electric": 1.2,
        "distance": 23.0,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 25",
        "installed_power_electric": 1.3,
        "distance": 24.0,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
    {
        "name": "Куст 26",
        "installed_power_electric": 1.5,
        "distance": 25.0,
        "load_factor_summer": 50,
        "load_factor_winter": 100,
        "type": WellCluster,
    },
]

objects = []
boiler_plants = []

for obj_data in objects_data:
    object_type = obj_data.pop("type")
    obj = object_type(**obj_data)
    objects.append(obj)

    boiler_plant = BoilerPlant(
        name=f"Котельная {obj.name}", fuel_type="ПНГ", fuel_heat_value=45
    )
    boiler_plants.append(boiler_plant)

for obj_data in well_clusters_data:
    object_type = obj_data.pop("type")
    obj = object_type(**obj_data)
    objects.append(obj)

fuel_cost = 1200  # Стоимость м3

model = HeatModel(objects=objects, boiler_plants=boiler_plants, fuel_cost=fuel_cost)

start_date = datetime.datetime(2024, 6, 1)
end_date = datetime.datetime(2028, 6, 1)
model.simulate(start_date, end_date)
