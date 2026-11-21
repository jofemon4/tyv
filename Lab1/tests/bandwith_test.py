import csv
import os
import time
from datetime import datetime
import numpy as np
import pyvisa
import serial
import matplotlib.pyplot as plt

RIGOL_RESOURCE = "USB0::0x0400::0x09C4::DG1D182202731::INSTR"
SERIAL_PORT = "COM3"  # Puerto COM3 del Arduino[cite: 3, 5]
BAUD_RATE = 115200  # Velocidad serie de 115200 baudios[cite: 3, 5]

SINE_AMPLITUDE_VPP = 2.0  # 2.0 Vpp dentro del rango unipolar de 0 a 5 V[cite: 3]
SINE_OFFSET_VDC = 2.5  # Centrado en 2.5 V con Vref = Vcc = 5 V[cite: 2]

# Frecuencias de barrido [Hz] (ajusta el rango superior según tu prescaler y Fs)
FREQUENCIES_HZ = np.geomspace(100, 2500000, num=200)

BURSTS_PER_FREQ = 4  # Ráfagas por frecuencia (ej. 4 * 500 = 2000 muestras por paso)
BURST_SIZE = 500

VREF = 5.0  # Referencia de tensión del ADC (Vcc = 5 V)[cite: 2]
ADC_MAX_CODE = 1023.0  # Salida de 10 bits (0 a 1023)[cite: 3]


def safe_write(inst, cmd, delay=0.05):
    """Envía un comando SCPI sin usar queries."""
    try:
        inst.write(cmd)
    except Exception:
        pass
    if delay > 0:
        time.sleep(delay)


def read_burst(ser, expected_count=BURST_SIZE, timeout_s=15.0):
    """Solicita una ráfaga ('b') al Arduino y devuelve (muestras, elapsed_us)."""
    ser.reset_input_buffer()
    ser.write(b"b")

    deadline = time.monotonic() + timeout_s
    header = ""
    while time.monotonic() < deadline:
        raw_line = ser.readline()
        if not raw_line:
            continue
        line = raw_line.decode("utf-8", errors="ignore").strip()
        if line.startswith("BURST "):
            header = line
            break

    if not header:
        raise TimeoutError("No se recibió cabecera BURST desde el Arduino.")

    parts = header.split()
    n_samples = int(parts[1])
    elapsed_us = float(parts[2])

    samples = []
    while len(samples) < n_samples and time.monotonic() < deadline:
        raw_line = ser.readline()
        if not raw_line:
            continue
        line = raw_line.decode("utf-8", errors="ignore").strip()
        if not line or line == "END":
            continue
        if line.isdigit():
            val = int(line)
            if 0 <= val <= 1023:
                samples.append(val)

    if len(samples) != expected_count:
        raise RuntimeError(
            f"Ráfaga incompleta: esperadas {expected_count}, recibidas {len(samples)}"
        )

    return np.array(samples, dtype=np.uint16), elapsed_us


def main():
    rm = pyvisa.ResourceManager()
    rigol = None
    ser = None

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, "outputs")
    os.makedirs(out_dir, exist_ok=True)

    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(out_dir, f"barrido_frecuencia_{timestamp_str}.csv")

    try:
        rigol = rm.open_resource(RIGOL_RESOURCE)
        rigol.timeout = 5000
        rigol.write_termination = "\n"
        rigol.read_termination = "\n"

        safe_write(rigol, "*CLS", 0.1)
        safe_write(rigol, "OUTP OFF", 0.05)  # Deshabilita salida al configurar[cite: 25, 48]
        safe_write(rigol, "OUTP:LOAD INF", 0.05)  # Alta impedancia de carga[cite: 48]
        safe_write(rigol, "VOLT:UNIT VPP", 0.05)  # Unidad en Vpp[cite: 20, 44]
        safe_write(
            rigol,
            f"APPL:SIN {FREQUENCIES_HZ[0]:.2f},{SINE_AMPLITUDE_VPP},{SINE_OFFSET_VDC}",
            0.1,
        )  # Senoidal en CH1 con frecuencia, amplitud y offset[cite: 26]
        safe_write(rigol, "OUTP ON", 0.3)  # Habilita salida[cite: 25, 48]

        ser = serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE, timeout=0.2)
        time.sleep(2.0)
        ser.reset_input_buffer()

        results = []

        with open(csv_filename, mode="w", newline="", encoding="utf-8") as f_csv:
            writer = csv.writer(f_csv, delimiter=";")
            writer.writerow(
                ["freq_hz", "burst_idx", "sample_idx", "adc_code", "voltage_v", "fs_burst_hz"]
            )

            for freq in FREQUENCIES_HZ:
                safe_write(rigol, f"FREQ {freq:.2f}", 0.15)  # Actualiza frecuencia en CH1[cite: 38, 39]

                freq_voltages = []
                freq_fs = []

                for b_idx in range(BURSTS_PER_FREQ):
                    codes, elapsed_us = read_burst(ser, expected_count=BURST_SIZE)
                    dt_s = elapsed_us * 1e-6
                    fs_burst = BURST_SIZE / dt_s if dt_s > 0 else 0.0
                    voltages = codes.astype(np.float64) * (VREF / ADC_MAX_CODE)

                    freq_voltages.append(voltages)
                    freq_fs.append(fs_burst)

                    for s_i, (c_val, v_val) in enumerate(zip(codes, voltages)):
                        writer.writerow([
                            f"{freq:.2f}",
                            b_idx,
                            s_i,
                            int(c_val),
                            f"{v_val:.6f}",
                            f"{fs_burst:.2f}",
                        ])

                all_v = np.concatenate(freq_voltages)
                ac_v = all_v - np.mean(all_v)
                # Amplitud estimada a partir del valor RMS de la componente alterna (sqrt(2) * RMS)
                amp_est_v = float(np.sqrt(2.0) * np.sqrt(np.mean(ac_v ** 2)))
                fs_avg = float(np.mean(freq_fs))

                results.append((freq, amp_est_v, fs_avg))
                print(
                    f"f = {freq:8.1f} Hz | Amplitud estimada = {amp_est_v:.4f} V | "
                    f"Fs media = {fs_avg / 1e3:.2f} kHz"
                )

        freqs = np.array([r[0] for r in results])
        amps = np.array([r[1] for r in results])
        ref_amp = amps[0] if len(amps) > 0 and amps[0] > 0 else 1.0
        gain_ratio = amps / ref_amp
        gain_db = 20.0 * np.log10(np.maximum(gain_ratio, 1e-12))

        print(f"\nCSV guardado en: {csv_filename}")

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.semilogx(freqs / 1e3, gain_db, marker="o", lw=1.2)
        ax.axhline(-3.0, color="r", linestyle="--", lw=1, label="-3 dB (0.707x)")
        # Referencia de mitad de tensión indicada en la guía de práctica (0.5x = -6.02 dB)[cite: 8]
        ax.axhline(20.0 * np.log10(0.5), color="g", linestyle=":", lw=1, label="0.5x (-6.02 dB)")
        ax.set_title("Respuesta en frecuencia del ADC (barrido senoidal)")
        ax.set_xlabel("Frecuencia [kHz]")
        ax.set_ylabel("Ganancia relativa [dB]")
        ax.legend()
        ax.grid(True, which="both")
        plt.tight_layout()
        plt.show()

    finally:
        if rigol is not None:
            safe_write(rigol, "OUTP OFF", 0.05)  # Deshabilita salida al cerrar[cite: 7, 48]
            try:
                rigol.close()
            except Exception:
                pass
        if ser is not None and ser.is_open:
            try:
                ser.close()
            except Exception:
                pass
        try:
            rm.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()