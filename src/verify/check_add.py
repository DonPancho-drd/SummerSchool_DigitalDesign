import numpy as np
from typing import List, Dict, Tuple


N = 4
VOLTAGE = 5.0
VTH = 1.5
RATIO = 0.3 # portion of a period from start where signal hasnot stabilize yet
DELAY = 100e-9
PERIOD = 500e-9
HALF_PERIOD = PERIOD / 2
TR = 20e-9
TF = 20e-9

# Порты: A[3:0] B[3:0] CIN ------- COUT[3:0] S[3:0]
INPUT_PORTS = 9
OUTPUT_PORTS = 8
COLS = INPUT_PORTS + OUTPUT_PORTS
CNT = 2 ** INPUT_PORTS

def to_digital(signal: float) -> int:

    if -VTH < signal < VTH:
        return 0
    elif VOLTAGE - VTH < signal < VOLTAGE + VTH:
        return 1

    raise ValueError(f"Forbidden signal value: {signal}")


def extract_plateau(plateau: List[Tuple[float, float]]) -> int:

    duration = plateau[-1][0] - plateau[0][0]
    if not (0 < duration <= HALF_PERIOD):
        raise ValueError(f"Wrong plateau duration: {duration}")

    stab_start = plateau[0][0] + (HALF_PERIOD-TF) * RATIO
    plateau = [point for point in plateau if point[0]>= stab_start]
    signal_values = np.array([point[1] for point in plateau])
    probabilities = np.array([(((plateau[i][0] - plateau[i-1][0]) / ((HALF_PERIOD-TF)*(1-RATIO))) if i!=0 else 0) for i in range(len(plateau))])
    #times = np.array([(plateau[i][0]) for i in range(len(plateau))])
    # # print(HALF_PERIOD-TF)
    #print(sum(probabilities))
    # print(signal_values)
    # # print(times)
    # print(probabilities)

    return to_digital(np.dot(signal_values, probabilities))

def process_output_signal(time: np.ndarray, signal: np.ndarray) -> np.ndarray:

    results = np.full(CNT, -1, dtype=int)
    plateau = []
    plateau_num = 0

    for point, value in zip(time, signal):
        if point <= DELAY:
            continue

        if plateau_num >= CNT:
            break

        if (DELAY + HALF_PERIOD * plateau_num + TF < point <=
            DELAY + HALF_PERIOD * (plateau_num + 1)):
            plateau.append((point, value))

        elif point > DELAY + HALF_PERIOD * (plateau_num + 1):
            if not plateau:
                raise ValueError(f"Empty plateau at position {plateau_num}")

            results[plateau_num] = extract_plateau(plateau)
            plateau.clear()
            plateau_num += 1


    if -1 in results:
        raise ValueError("Missing plateaus in output signal")
    return results

def process_input_signal(time: np.ndarray, signal: np.ndarray, period: float) -> np.ndarray:

    results = np.full(CNT, -1, dtype=int)
    plateau_num = 0

    for point, value in zip(time, signal):
        if point <= DELAY:
            continue

        if plateau_num >= CNT or point >= DELAY + CNT * HALF_PERIOD:
            break

        if (results[plateau_num] == -1 and
            DELAY + HALF_PERIOD * plateau_num + TR < point <
            DELAY + HALF_PERIOD * (plateau_num + 1)):
            results[plateau_num] = to_digital(value)
            plateau_num += 1

    if -1 in results:
        raise ValueError("Missing plateaus in input signal")
    return results

def main():

    try:
        data = np.loadtxt('fa1_4bit.txt', skiprows=1)
        if data.size == 0:
            raise ValueError("Input file is empty")

        time = data[:, 0]
        signals = data[:, 1:]


    except Exception as e:
        print(f"Error loading data: {e}")
        return


    pulse_params = [
        {
            'period': (2 ** i) * PERIOD,
            'tr': TR,
            'tf': TF,
            'name': f'A[{i}]' if i < N else f'B[{i-N}]' if i < 2*N else 'Cin'
        }
        for i in range(INPUT_PORTS)
    ]


    signal_results = np.zeros((CNT, COLS), dtype=int)


    for i, param in enumerate(pulse_params):
        print(f"\nАнализ входного сигнала {param['name']}")
        try:
            signal_results[:, i] = process_input_signal(
                time, signals[:, i], param['period']
            )
        except Exception as e:
            print(f"Error processing {param['name']}: {e}")
            return


    for i in range(INPUT_PORTS, COLS):
        signal_name = f"Cout[{i-INPUT_PORTS}]" if i < INPUT_PORTS+N else f"S[{i-INPUT_PORTS-N}]"
        print(f"\nАнализ выходного сигнала {signal_name}")
        try:
            signal_results[:, i] = process_output_signal(time, signals[:, i])
        except Exception as e:
            print(f"Error processing {signal_name}: {e}")
            return


    try:

        bit_data = {
            'A': {i: signal_results[:, i] for i in range(N)},
            'B': {i: signal_results[:, i+N] for i in range(N)},
            'Cin': {i: signal_results[:, 2*N] if i==0 else np.zeros((CNT), dtype=int) for i in range(N)},
            'Cout': {i: signal_results[:, 2*N+1+i] for i in range(N)},
            'S': {i: signal_results[:, 3*N+1+i] for i in range(N)}
        }

        for i in range(CNT):
            Cin = int(bit_data['Cin'][0][i])

            for n in range(N):
                A = int(bit_data['A'][n][i])
                B = int(bit_data['B'][n][i])


                S = A ^ B ^ Cin
                Cout = (A & B) | (A & Cin) | (Cin & B)



                if bit_data['S'][n][i] != S:
                    print(f"Ошибка суммы в строке {i}, разряд {n}: ожидалось {S}, получено {bit_data['S'][n][i]}")

                if bit_data['Cout'][n][i] != Cout:
                    print(f"Ошибка переноса в строке {i}, разряд {n}: ожидалось {Cout}, получено {bit_data['Cout'][n][i]}")

                Cin = Cout

                if n < N-1:
                    bit_data['Cin'][n+1][i] = Cin

        print("\nПроверка завершена успешно!")

    except Exception as e:
        print(f"Ошибка при проверке сумматора: {e}")

if __name__ == "__main__":
    main()
