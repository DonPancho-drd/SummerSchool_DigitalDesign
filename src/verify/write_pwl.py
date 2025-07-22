def generate_pwl_file(filename, params, num_cycles=1):
    """
    Генерирует PWL файл для LTspice

    Parameters:

            - v1: Начальное напряжение (V)
            - v2: Пиковое напряжение (V)
            - td: Задержка перед первым импульсом (s)
            - tr: Время нарастания (s)
            - tf: Время спада (s)
            - pw: Длительность импульса (s)
            - per: Период (s)
            - num: Количество повторений (для PULSE)
        num_cycles (int): Количество циклов для PWL
    """

    v1 = params.get('v1', 0)
    v2 = params.get('v2', 5)
    td = params.get('td', 100e-9)
    tr = params.get('tr', 20e-9)
    tf = params.get('tf', 20e-9)
    pw = params.get('pw', 230e-9)
    per = params.get('per', 500e-9)

    with open(filename, 'w') as f:


        f.write(f"{0:.12e} {v1:.6f}\n")
        f.write(f"{td:.12e} {v1:.6f}\n")

        for i in range(num_cycles):

            t_start = td + i*per
            f.write(f"{t_start:.12e} {v1:.6f}\n")
            f.write(f"{(t_start + tr):.12e} {v2:.6f}\n")

            # Импульс
            t_high = t_start + tr + pw
            f.write(f"{t_high:.12e} {v2:.6f}\n")

            # Задний фронт
            t_end = t_high + tf
            f.write(f"{t_end:.12e} {v1:.6f}\n")

            # Пауза до следующего импульса
            if i < num_cycles - 1:
                f.write(f"{(td + (i+1)*per):.12e} {v1:.6f}\n")



if __name__ == "__main__":

    pulse_params = {
        'v1': 0,
        'v2': 5,
        'td': 100e-9,
        'tr': 20e-9,
        'tf': 20e-9,
        'pw': 230e-9,
        'per': 500e-9
    }

    generate_pwl_file("pulse_signal.pwl", pulse_params, num_cycles=5)
