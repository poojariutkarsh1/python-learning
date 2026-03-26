# Ultrasonic Sensor Data Filtering using NumPy

## 📌 Project Overview

This project demonstrates how to collect real-time distance data from an ultrasonic sensor using an Arduino and process it in Python to remove noise using a median filter.

Ultrasonic sensors often produce noisy readings due to environmental factors. This project applies a simple but effective filtering technique to improve the reliability of the measured data.

---

## 🎯 Objectives

* Read real-time sensor data from Arduino using serial communication
* Store and process the data in Python
* Apply a median filter to remove noise (spikes)
* Compare raw and filtered data

---

## 🛠️ Technologies Used

* Python
* NumPy
* PySerial
* Arduino (Ultrasonic Sensor - HC-SR04)

---

## 🔌 System Workflow

1. Arduino measures distance using the ultrasonic sensor
2. Data is sent to the computer via serial communication
3. Python reads the incoming data
4. Data is stored in a list
5. A sliding window median filter is applied
6. Filtered data is compared with raw data

---

## 🧠 Filtering Logic

A **median filter** is used to remove noise.

* A small window (e.g., 5 values) is taken from the dataset
* The values are sorted
* The middle value (median) is selected
* This process is repeated across the dataset

### Example:

Raw data:
[30, 31, 29, 150, 30]

Sorted:
[29, 30, 30, 31, 150]

Filtered value:
30 (spike removed)

---

## 📊 Key Observations

* Sudden spikes (noise) are reduced effectively
* Filtered data is smoother and more stable
* Larger window size increases smoothness but introduces delay

---

## ⚙️ How to Run

### 1. Install dependencies

```bash
pip install pyserial numpy
```

### 2. Upload Arduino code

Ensure Arduino sends distance values via Serial at 9600 baud.

### 3. Update COM Port

In Python code:

```python
ser = serial.Serial('COM3', 9600)
```

(Change COM port accordingly)

### 4. Run Python script

```bash
python main.py
```

---

## 📌 Output

* Raw sensor readings printed in real-time
* Filtered values displayed alongside raw values
* Spike count comparison before and after filtering

---

## ⚠️ Notes

* Ensure Arduino Serial Monitor is closed before running Python
* Filtering reduces data length due to window processing
* Noise detection depends on chosen threshold

---

## 🚀 Future Improvements

* Real-time filtering (live smoothing)
* Graph visualization (Matplotlib)
* Adaptive filtering techniques
* Integration with machine learning models

---

## 🧭 Conclusion

This project demonstrates a simple yet powerful approach to handling noisy sensor data. It highlights the importance of preprocessing in real-world data systems and serves as a foundation for more advanced signal processing and machine learning applications.

---
