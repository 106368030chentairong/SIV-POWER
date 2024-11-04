# Automatic Power Supply Control and Oscilloscope Measurement System

This project automates power supply voltage output control, uses an oscilloscope to measure the output voltage of a circuit board, calculates the power efficiency of the circuit, and analyzes harmonic distortion.

## Features

- **Power Supply Control**: Automatically adjust the output voltage of a connected power supply via communication protocols like SCPI (Standard Commands for Programmable Instruments) or custom serial commands.
- **Oscilloscope Measurement**: Automate oscilloscope measurements to capture output voltage waveform and data from a circuit board under test.
- **Efficiency Calculation**: Measure and calculate the efficiency of the power supply by analyzing input/output voltage and current.
- **Harmonic Distortion Analysis**: Perform harmonic analysis on the output voltage waveform to calculate Total Harmonic Distortion (THD).

## Project Structure

```bash
.
├── lib/                     # Source code for automation and control
│   ├── power_supply_control.py  # Script for controlling the power supply
│   ├── oscilloscope_control.py  # Script for controlling the oscilloscope
│   ├── efficiency_calculator.py # Script for calculating power efficiency
│   └── harmonic_analysis.py     # Script for harmonic distortion analysis
├── docs/                    # Documentation and guides
├── requirements.txt         # Python dependencies
└── README.md                # Project overview (this file)
```

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/your-username/auto-power-supply-control.git
    cd auto-power-supply-control
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Power Supply Control

The `power_supply_control.py` script communicates with the power supply to set and adjust the voltage output. You can specify the desired output voltage as a parameter.

```bash
python lib/power_supply_control.py --voltage 5.0
```

### 2. Oscilloscope Measurement

The `oscilloscope_control.py` script automates the measurement of output voltage using an oscilloscope. It captures waveform data and can export the results to a CSV file.

```bash
python lib/oscilloscope_control.py --capture --output waveform.csv
```

### 3. Efficiency Calculation

The `efficiency_calculator.py` script calculates the efficiency of the power supply by comparing input and output voltage and current measurements.

```bash
python lib/efficiency_calculator.py --input_voltage 12 --input_current 2 --output_voltage 5 --output_current 1
```

### 4. Harmonic Distortion Analysis

The `harmonic_analysis.py` script performs a Fast Fourier Transform (FFT) on the captured waveform data to analyze and calculate Total Harmonic Distortion (THD).

```bash
python lib/harmonic_analysis.py --input waveform.csv
```

## Dependencies

- Python 3.x
- Libraries:
    - `pyvisa` (for instrument communication)
    - `numpy` (for numerical analysis)
    - `scipy` (for FFT and signal processing)
    - `matplotlib` (for plotting waveforms)
    - `pandas` (for CSV data handling)

Install dependencies via:
```bash
pip install -r requirements.txt
```

## Example Workflow

1. Control the power supply to set the desired voltage.
2. Use the oscilloscope to measure the output voltage waveform.
3. Calculate the power efficiency of the circuit.
4. Perform harmonic distortion analysis on the output signal.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any bugs or feature requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
