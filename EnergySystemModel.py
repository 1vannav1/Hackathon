# файл: EnergySystemModel.py

import datetime

class EnergySystemModel:
    def __init__(self, consumers, network, power_plant):
        """
        consumers: список (или другой контейнер) объектов-потребителей,
                   у которых есть метод calculate_power_demand(date_time) -> float (МВт).
        network:   объект модели сети (NetworkGridModel), где есть метод calc_generation_needed.
        power_plant: объект модели ГТЭС (GTESModel), где есть метод generate().
        """
        self.consumers = consumers
        self.network = network
        self.power_plant = power_plant

        # Для накопления итоговых результатов:
        self.total_fuel_consumption = 0.0
        self.total_power_generated = 0.0
        self.total_power_consumed = 0.0
        self.total_unserved = 0.0  # Сколько не смогли покрыть, если такое возможно

        # Затраты на персонал, ТО/КР, и т.д. можно суммировать,
        # если у power_plant/network есть соответствующие поля
        self.total_salary_cost = 0.0
        self.total_maintenance_cost = 0.0

    def simulate(self, start_date, end_date, time_step_hours=1):
        """
        Почасовая модель:
        1) Суммируем нагрузку потребителей
        2) Модель сети считает, сколько МВт нужно выдать, учитывая потери, PF и т.п.
        3) ГТЭС генерирует (с учётом состояния ГТУ)
        4) Снова учитываем фактический отпуск, считаем реальное покрытие спроса
        5) Накопление итоговых показателей
        """

        current_time = start_date
        last_month = None

        while current_time <= end_date:
            # -- (1) Сбор нагрузки всех потребителей --
            total_consumers_load_mw = 0.0
            for consumer in self.consumers:
                demand_mw = consumer.calculate_power_demand(current_time)
                total_consumers_load_mw += demand_mw

            # -- (2) Сеть считает требуемую генерацию (учитывая потери, PF и т.д.) --
            required_generation_mw = self.network.calc_generation_needed(
                total_consumers_load_mw,
                current_time
            )
            # Здесь, при желании, можно получить и потребную мощность в МВА,
            # если network внутри учитывает cosφ = 0.97 и т.д.

            # -- (3) ГТЭС пытается выдать запрошенную мощность --
            actual_generation_mw, fuel_consumed = self.power_plant.generate(
                required_generation_mw,
                current_time
            )

            # Суммируем общий расход топлива
            self.total_fuel_consumption += fuel_consumed

            # -- (4) Фактическое покрытие нагрузки + учёт потерь --
            # Для простоты допустим, что всё, что выдала ГТЭС, сеть смогла довести до потребителей
            # (считая, что потери уже были заложены в required_generation_mw).
            # Если хотим обратно проверить "достаточно ли" подали, можно условно сказать:
            if actual_generation_mw < required_generation_mw:
                # Не хватает для полной компенсации
                # Потребители могут недополучить часть энергии.
                # Но как распределять недопоставку — отдельный вопрос (пропорционально?)
                unserved = required_generation_mw - actual_generation_mw
                self.total_unserved += unserved
                # Тогда фактическое потребление снизилось
                actual_consumption = total_consumers_load_mw - unserved
            else:
                unserved = 0.0
                actual_consumption = total_consumers_load_mw

            self.total_power_generated += actual_generation_mw
            self.total_power_consumed += actual_consumption

            # -- (5) Учёт расходов на персонал, ТО/КР и т.п. --
            # Можно раз в месяц (при переходе месяца) увеличивать total_salary_cost
            if current_time.month != last_month:
                last_month = current_time.month
                # Допустим, в power_plant хранится zp = 150000*20,
                # а в network хранится zp = 130000*30
                self.total_salary_cost += (self.power_plant.personnel_salary
                                           + self.network.personnel_salary)
                # ТО/КР: если внутри power_plant есть счётчик total_maintenance_cost
                self.total_maintenance_cost += self.power_plant.total_maintenance_cost
                # (затем обнуляем в power_plant, если нужно, или храним нарастающим итогом)

            # -- Двигаем время --
            current_time += datetime.timedelta(hours=time_step_hours)

        # После цикла выводим итоги
        self.print_summary()

    def print_summary(self):
        print("=== Итог EnergySystemModel ===")
        print(f"Суммарная генерация: {self.total_power_generated:.2f} МВт*ч")
        print(f"Суммарное потребление: {self.total_power_consumed:.2f} МВт*ч")
        print(f"Непокрытый спрос: {self.total_unserved:.2f} МВт*ч")
        print(f"Общий расход топлива (ПНГ/СОГ): {self.total_fuel_consumption:.2f} м3")
        print(f"Итоговые расходы на ЗП: {self.total_salary_cost:.2f} руб.")
        print(f"Итоговые расходы на ТО/КР: {self.total_maintenance_cost:.2f} руб.")
