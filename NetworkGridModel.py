import datetime


class GTU:
    def __init__(self, id, specs, average_load_factor=None):
        # Идентификатор для обращения к ГТУ (задача загрузки в том числе)
        self.id = id
        self.specs = specs  # Задает словарь характеристик, как в ТЗ
        self.average_load_factor = average_load_factor  # Как раз коэф загрузки от 0 до 1
        self.total_run_hours = 0  # Общее время работы ГТУ
        # Время с последнего ТО. После ТО оно сбрасывается и также увеличивает число ТО на 1
        self.run_hours = 0
        self.hours_since_kr = 0  # Время с последнего КР, аналогично ТО
        self.status = "работает"  # Начальное положение всех ГТУ не в резерве для слежения
        self.next_to = None  # Дата следующегго ТО, задается по моточасам в симуляции
        self.next_kr = None  # Аналогично КР
        self.end_maintenance = None  # Окончание обслуживания
        self.to_counter = 0    # Счетчик ТО
        self.kr_counter = 0    # Счетчик КР
        self.downtime_hours = 0  # Общее время простоя в часах
        self.maintenance_cost = 0.0  # Расходы на ТО и КР ГТУ

    def __repr__(self):  # Функция для выдачи информации об конкретном ГТУ
        return f"GTU(ID: {self.id}, Status: {self.status}, Total Run Hours: {self.total_run_hours}, Run Hours: {self.run_hours}, Load: {self.average_load_factor}, TO: {self.to_counter}, KR: {self.kr_counter}, Downtime: {self.downtime_hours}, Maintenance Cost: {self.maintenance_cost})"


class GTESModel:
    prise_per_MW = 5.6

    def __init__(self, gtu_specs, load_factors):
        self.gtu_specs = gtu_specs  # Сохраняет значения параметров ГТУ в системе ГТЭС
        self.gtus = [GTU(i, gtu_specs, load_factors[i]) for i in range(
            # Создает в модели отдельные объекты ГТУ с уникальными ID
            gtu_specs['кол-во'])]
        self.hot_reserve = None  # Горячий резерв
        self.cold_reserve = None  # Холодный резерв
        self.total_energy_generated = 0.0
        self.start_date = None  # Начало моделирования
        self.end_date = None

        # Эксплуатационные расходы
        self.personnel_salary = 150000 * 20  # Зарплата 20 человек в месяц
        self.total_salary_cost = 0.0  # Общие расходы на зарплату
        self.total_maintenance_cost = 0.0  # Общие расходы на ТО и КР

        # Связка со след. функцией, принимает определенный ГТУ как горячий резерв
        self.assign_hot_reserve()
        self.assign_cold_reserve()  # Аналогично с холодным

    def assign_hot_reserve(self):
        # Выбор горячего резерва. Я выбрал условие по загрузке выше 0 но ниже 0,15
        eligible_gtus = [gtu for gtu in self.gtus if gtu.status == "работает" and 0 <
                         # Выбор ГТУ в резерв, оно работает и слабо загружено
                         gtu.average_load_factor < 0.15]
        if eligible_gtus:
            # выбираем минимально отработавший резерв
            self.hot_reserve = min(
                eligible_gtus, key=lambda x: x.total_run_hours)
            self.hot_reserve.status = "горячий_резерв"
        else:
            self.hot_reserve = None

    def assign_cold_reserve(self):
        # Тут холодный резерв. Все аналогично, но загрузка в простое 0
        eligible_gtus = [gtu for gtu in self.gtus if gtu.status ==
                         "работает" and gtu.average_load_factor == 0]
        if eligible_gtus:
            self.cold_reserve = min(
                eligible_gtus, key=lambda x: x.total_run_hours)
            self.cold_reserve.status = "холодный_резерв"
        else:
            self.cold_reserve = None

    def perform_maintenance(self, gtu, current_time):
        # Перевод ГТУ на ТО или КР
        if gtu.run_hours >= self.gtu_specs['ТО_периодичность'] and gtu.status == "работает":
            # Визуализация вывода в ТО
            # print(f"GTU {gtu.id} уходит на ТО в {current_time}")
            gtu.status = "ТО"
            # Время ТО принял 3 дня, меняется легко
            to_duration = datetime.timedelta(hours=3*24)
            gtu.end_maintenance = current_time + to_duration  # Время завершения ТО
            gtu.next_to = current_time + to_duration

            gtu.downtime_hours += to_duration.total_seconds() / 3600  # Время простоя в часах
            gtu.to_counter += 1  # Счетчик ТО
            gtu.run_hours = 0  # Сброс времени до следующего ТО
            # Стоимость ТО для GTU, в расходы
            gtu.maintenance_cost += self.gtu_specs['ТО_стоимость']
            # Общая стоимость эксплуатации
            self.total_maintenance_cost += self.gtu_specs['ТО_стоимость']

            return True
        # Все аналогично для КР
        elif gtu.hours_since_kr >= self.gtu_specs['КР_периодичность'] and gtu.status == "работает":
            print(f"GTU {gtu.id} уходит на КР в {current_time}")
            gtu.status = "КР"
            kr_duration = datetime.timedelta(hours=7*24)  # 7 дней
            gtu.end_maintenance = current_time + kr_duration
            gtu.next_kr = current_time + kr_duration
            gtu.downtime_hours += kr_duration.total_seconds() / 3600
            gtu.kr_counter += 1
            gtu.hours_since_kr = 0
            gtu.maintenance_cost += self.gtu_specs['КР_стоимость']
            self.total_maintenance_cost += self.gtu_specs['КР_стоимость']
            return True
        return False

    def update_status(self, gtu, current_time):
        # Проверка времени ТО и КР, возвращение в эксплуатацию
        if gtu.status in ["ТО", "КР"] and current_time >= gtu.end_maintenance:
            # print(f"GTU {gtu.id} возвращается в строй в {current_time}")
            gtu.status = "работает"
            gtu.next_to = None
            gtu.next_kr = None
            gtu.end_maintenance = None

            return True
        return False

    def simulate(self, start_date, end_date):  # Собстна, сама симуляция
        self.start_date = start_date
        self.end_date = end_date
        current_time = start_date
        last_month = None

        while current_time <= end_date:  # Расчет электроэнергии и времени работы
            for gtu in self.gtus:
                if gtu.status == "работает" or gtu.status == "горячий_резерв":
                    hours_this_step = 1  # Шаг моделирования, 1 час по ТЗ
                    # Для моточасов я учел как произведение времени в часах на коэф загрузки
                    effective_hours = gtu.average_load_factor * hours_this_step
                    gtu.total_run_hours += effective_hours  # Общее время работы
                    gtu.run_hours += effective_hours  # Время с ТО
                    gtu.hours_since_kr += effective_hours  # Время с КР
                    if gtu.status == "работает":
                        # Проверка статуса и вычисление выработанной энергии
                        self.total_energy_generated += gtu.specs['мощность'] * \
                            gtu.average_load_factor * hours_this_step
                    elif gtu.status == "горячий_резерв":
                        self.total_energy_generated += gtu.specs['мощность'] * \
                            gtu.average_load_factor * hours_this_step

            # Проверка статуса ТО и КР, ввод резервов
            need_maintenance = []  # Список ГТУ ТО и КР
            for gtu in self.gtus:
                if self.perform_maintenance(gtu, current_time):
                    need_maintenance.append(gtu)

            hot_reserve_used = False  # Ограничение для разового использования горячего резерва
            for gtu in need_maintenance:
                if not hot_reserve_used and self.hot_reserve and self.hot_reserve.status == "горячий_резерв":
                    # print(f"  Замена GTU {gtu.id} на GTU {self.hot_reserve.id} (горячий резерв)")
                    self.hot_reserve.status = "работает"
                    hot_reserve_used = True  # На этом шаге больше нельзя использовать резерв после ввода ТО
                    self.assign_hot_reserve()  # Поиск иных резервов

                # Если горячий использован, вводим холодный
                elif self.cold_reserve and self.cold_reserve.status == 'холодный_резерв':
                    # print(f"  Замена GTU {gtu.id} на GTU {self.cold_reserve.id} (холодный резерв)")
                    self.cold_reserve.status = "работает"
                    self.assign_cold_reserve()
                # else:
                #     # Если все резервы кончились
                #     print(f"  Нет доступных резервов для замены GTU {gtu.id}")

            # Обновление статусов ГТУ
            for gtu in self.gtus:
                self.update_status(gtu, current_time)

            # Расход на зарплату, считает по первому числу месяца
            if current_time.month != last_month:
                self.total_salary_cost += self.personnel_salary
                last_month = current_time.month

            current_time += datetime.timedelta(hours=1)

        # Вывод итоговой информации по каждой ГТУ
        print("\nИтоговая информация:")

        # for gtu in self.gtus:
        #     print(f"  GTU {gtu.id}:")
        #     print(f"   Выработка: {gtu.specs['мощность'] * gtu.average_load_factor * gtu.total_run_hours:.2f} МВт*ч")
        #     print(f"   Общее время работы: {gtu.total_run_hours:.2f}")
        #     print(f"   ТО: {gtu.to_counter}")
        #     print(f"   КР: {gtu.kr_counter}")
        #     print(f"   Простой: {gtu.downtime_hours:.2f} часов")
        #     print(f"   Расходы на ТО и КР: {gtu.maintenance_cost:.2f} руб.")

        # Итоговые расходы
        print(
            f"\nИтоговые расходы на зарплату: {self.total_salary_cost:.2f} руб.")
        print(
            f"Итоговые расходы на ТО и КР: {self.total_maintenance_cost:.2f} руб.")
        print(
            f"Суммарная выработка электроэнергии: {self.total_energy_generated:.2f} МВт*ч")
        cost_electricity = self.total_energy_generated * self.prise_per_MW
        print(
            f"Суммарная стоймость электроэнергии: {cost_electricity:.2f} руб")
        res = cost_electricity + self.total_maintenance_cost + self.total_salary_cost
        print(f"{res:.2f}")

# _________________________________________________________________________________________
# добавил для связи между файлами. Оставил минимум, который мне необходим. При желании нужно изменить


class GridModel:
    # Установка коэффициента загрузки
    def __init__(self):
        self.load_factors = [0.6, 0.7, 0.5, 0.8, 0.05, 0.75, 0.8, 0.85, 0.0]
        self.total_salary_cost = 0

    def set_load(self, new_load_factors):
        self.load_factors = new_load_factors

    def get_load(self):
        return self.load_factors

    # получение результирующей стоимости. Пока оставим так но нужно переписать
    def set_salary_cost(self, cost):
        self.total_salary_cost = cost

    def get_salary_cost(self):
        return self.total_salary_cost


grid_model = GridModel()
# _________________________________________________________________________________________


# Тут само моделирование с нашими данным
gtu_specs = {
    'мощность': 16,
    'кол-во': 9,
    'ТО_периодичность': 1500,
    'ТО_стоимость': 15000000,
    'КР_периодичность': 10000,
    'КР_стоимость': 75000000,
    'время_запуска_из_холодного_резерва': 2
}

# Тут моделирование с резервами, ГТУ 4 горячий, ГТУ 8 холодный
load_factors = grid_model.get_load()

model = GTESModel(gtu_specs, load_factors)

start_date = datetime.datetime(2024, 6, 1)
end_date = datetime.datetime(2025, 6, 1)
model.simulate(start_date, end_date)
