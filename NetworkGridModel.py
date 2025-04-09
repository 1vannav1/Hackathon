import datetime
import math

class PowerConsumer:
    def __init__(self, name, installed_power_electric, distance, load_factor_summer, load_factor_winter, voltage = 10):
        self.name = name
        self.installed_power_electric = installed_power_electric
        self.distance = distance
        self.load_factor_summer = load_factor_summer / 100 
        self.load_factor_winter = load_factor_winter / 100
        self.power_factor = 0.97  
        self.heating_load = 0  
        self.voltage = voltage
        self.total_power_consumption = 0 

    def calculate_power_demand(self, date):

        hours_in_day = 1 
        if 6 <= date.month <= 9:
            power_demand = self.installed_power_electric * self.load_factor_summer * 1000 
        else:
            power_demand = self.installed_power_electric * self.load_factor_winter * 1000 
        return power_demand

    def __repr__(self):
        return f"{self.name} (Установленная мощность: {self.installed_power_electric} МВт, Расстояние: {self.distance} км, Потреблено: {self.total_power_consumption:.2f} МВт*ч)" #Общее потребление

class ProductionFacility(PowerConsumer):

    def __init__(self, name, installed_power_electric, heating_load, distance, load_factor_summer, load_factor_winter, voltage = 10):
        super().__init__(name, installed_power_electric, distance, load_factor_summer, load_factor_winter, voltage)
        self.heating_load = heating_load

class LivingComplex(PowerConsumer):

    def __init__(self, name, installed_power_electric, heating_load, distance, load_factor_summer, load_factor_winter, voltage = 10):
        super().__init__(name, installed_power_electric, distance, load_factor_summer, load_factor_winter, voltage)
        self.heating_load = heating_load

class WellCluster(PowerConsumer):

    def __init__(self, name, installed_power_electric, distance, load_factor_summer, load_factor_winter, voltage = 10):
        super().__init__(name, installed_power_electric, distance, load_factor_summer, load_factor_winter, voltage)

class PowerLine:

    def __init__(self, source, destination, length, material="AC-120/19", voltage=10, r0 = 0.244, x0 = 0.414):
        self.source = source #Откуда
        self.destination = destination #Куда
        self.length = length #км
        self.material = material #Материал провода
        self.voltage = voltage #кВ
        self.personnel_count = 30
        self.personnel_salary = 130000
        self.power_loss = 0 #Вт
        self.total_power_loss = 0 
        self.r0 = r0 #Ом/км
        self.x0 = x0 #Ом/км
        self.voltage_drop = 0 #В

    def calculate_power_loss(self, power_transmitted_hourly, power_factor = 0.97):
        #Полное сопротивление линии (Ом)
        r = self.r0 * self.length
        x = self.x0 * self.length
        z = math.sqrt(r**2 + x**2)

        #Ток в линии (А)
        i = (power_transmitted_hourly) / (math.sqrt(3) * self.voltage * 1000 * power_factor) 

        #Потери мощности (Вт)
        self.power_loss = 3 * i**2 * r 

        #Падение напряжения (В)
        self.voltage_drop = (i * z)

        return self.power_loss

    def __repr__(self):
        return f"Линия электропередачи ГТЭС -> {self.destination.name} (Длина: {self.length} км, Напряжение: {self.voltage} кВ, Потери мощности: {self.power_loss:.2f} Вт, Общие потери электроэнергии: {self.total_power_loss:.2f} кВт*ч, Падение напряжения: {self.voltage_drop:.2f} В)" #Изменил в Вт и убрал мощность

class PowerPlant:

    def __init__(self, name="ГТЭС"):
        self.name = name

class PowerGridModel:
    def __init__(self, consumers):
        self.consumers = consumers
        self.power_lines = [] #Список линий электропередач
        self.total_power_loss_w = 0 #Суммарные потери мощности в Вт
        self.total_power_loss_kwh = 0 #Потери кВт*ч
        self.total_power_loss_mwh = 0 #Итоговые потери в МВт*ч
        self.personnel_salary = 130000 * 30 

    def create_power_lines(self):
        powerplant = PowerPlant() 

        for consumer in self.consumers:
            line = PowerLine(powerplant, consumer, consumer.distance, voltage = consumer.voltage)
            self.power_lines.append(line)

    def simulate(self, start_date, end_date):

        total_hours = (end_date - start_date).total_seconds() / 3600
        self.create_power_lines() #Создаем линии электропередач
        current_date = start_date
        last_month = None 
        self.total_personnel_cost = 0 #Расход ЗП

        while current_date <= end_date:

            total_power_demand = 0
            for consumer in self.consumers:
                power_demand_kw = consumer.calculate_power_demand(current_date)  
                consumer.total_power_consumption += power_demand_kw  / 1000 

                total_power_demand += power_demand_kw 

            power_loss_sum = 0 
            for line in self.power_lines:
                power_transmitted_hourly = line.destination.calculate_power_demand(current_date)
                power_loss = line.calculate_power_loss(power_transmitted_hourly) 

                line_power_loss_kwh = power_loss * total_hours / 1000
                line.total_power_loss = line_power_loss_kwh

                power_loss_sum += power_loss

     
            if current_date.month != last_month:
                self.total_personnel_cost += self.personnel_salary 
                last_month = current_date.month

            current_date += datetime.timedelta(hours=1) 

        self.total_power_loss_w = power_loss_sum
        self.total_power_loss_kwh = power_loss_sum * total_hours / 1000
        self.total_power_loss_mwh = self.total_power_loss_kwh / 1000

        print("---Результаты моделирования---")
        print(f"Суммарные потери мощности: {self.total_power_loss_w:.2f} Вт")
        print(f"Общие потери электроэнергии за весь период: {self.total_power_loss_mwh:.2f} МВт*ч") #Потери за весь период
        print(f"Общая сумма расходов на ЗП персонала: {self.total_personnel_cost:.2f} руб.")

        print("\n---Состояние объектов---")
        for consumer in self.consumers:
            print(consumer)

        print("\n---Состояние линий электропередач---")
        for line in self.power_lines:
            print(line)

objects_data = [
    {"name": "УКПГ", "installed_power_electric": 30.0, "heating_load": 3.04, "distance": 0.50, "load_factor_summer": 90, "load_factor_winter": 95, "type": ProductionFacility, "voltage": 10},
    {"name": "ОБП", "installed_power_electric": 9.0, "heating_load": 0.64, "distance": 3.0, "load_factor_summer": 80, "load_factor_winter": 90, "type": ProductionFacility, "voltage": 10},
    {"name": "ВЖК", "installed_power_electric": 2.0, "heating_load": 0.35, "distance": 3.50, "load_factor_summer": 100, "load_factor_winter": 100, "type": LivingComplex, "voltage": 10},
    {"name": "ПЖК", "installed_power_electric": 3.0, "heating_load": 2.58, "distance": 4.0, "load_factor_summer": 100, "load_factor_winter": 100, "type": LivingComplex, "voltage": 10},
    {"name": "ПСП", "installed_power_electric": 10.0, "heating_load": 1.91, "distance": 100.0, "load_factor_summer": 100, "load_factor_winter": 100, "type": ProductionFacility, "voltage": 10},
]

well_clusters_data = [
    {"name": "Куст 1", "installed_power_electric": 0.7, "distance": 1.0, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster, "voltage": 10},
    {"name": "Куст 2", "installed_power_electric": 0.8, "distance": 2.0, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 3", "installed_power_electric": 0.5, "distance": 3.0, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 4", "installed_power_electric": 0.9, "distance": 3.3, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 5", "installed_power_electric": 1.0, "distance": 4.0, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 6", "installed_power_electric": 0.9, "distance": 4.5, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 7", "installed_power_electric": 0.5, "distance": 5.0, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 8", "installed_power_electric": 1.0, "distance": 5.2, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 9", "installed_power_electric": 1.3, "distance": 5.7, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 10", "installed_power_electric": 1.0, "distance": 6.0, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 11", "installed_power_electric": 0.8, "distance": 6.5, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 12", "installed_power_electric": 0.6, "distance": 7.0, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 13", "installed_power_electric": 0.8, "distance": 7.5, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 14", "installed_power_electric": 1.0, "distance": 7.8, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 15", "installed_power_electric": 1.0, "distance": 8.0, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 16", "installed_power_electric": 0.7, "distance": 8.5, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 17", "installed_power_electric": 1.0, "distance": 9.0, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 18", "installed_power_electric": 0.8, "distance": 9.3, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 19", "installed_power_electric": 1.0, "distance": 9.7, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 20", "installed_power_electric": 1.1, "distance": 17.0, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 21", "installed_power_electric": 1.0, "distance": 18.0, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
    {"name": "Куст 22", "installed_power_electric": 2.2, "distance": 20.0, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
 {"name": "Куст 23", "installed_power_electric": 1.4, "distance": 22.0, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
 {"name": "Куст 24", "installed_power_electric": 1.2, "distance": 23.0, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
 {"name": "Куст 25", "installed_power_electric": 1.3, "distance": 24.0, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster},
 {"name": "Куст 26", "installed_power_electric": 1.5, "distance": 25.0, "load_factor_summer": 50, "load_factor_winter": 100, "type": WellCluster}
]

consumers = []

for obj_data in objects_data:
  object_type = obj_data.pop("type")
  obj = object_type(**obj_data)
  consumers.append(obj)

for obj_data in well_clusters_data:
  object_type = obj_data.pop("type")
  obj = object_type(**obj_data)
  consumers.append(obj)

model = PowerGridModel(consumers=consumers)

start_date = datetime.datetime(2024, 6, 1)
end_date = datetime.datetime(2024, 6, 2)
model.simulate(start_date, end_date)