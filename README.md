# CIC-IDS2017 Intrusion Detection System

This project focuses on building a state-of-the-art machine learning-based intrusion detection system using the **CICIDS 2017 dataset**.
The goal is to classify network traffic as benign or malicious and identify different types of attacks in real-time.

---

## 🌟 Key Features

- **Real-Time Dash UI:** A modern, premium Dark Mode dashboard built with Plotly Dash and Dash Bootstrap Components.
- **OpenLDAP Security:** The Network Admin portal is secured via OpenLDAP authentication.
- **Live Traffic Streaming:** Analyzes incoming network packets using a pre-trained XGBoost/Scikit-Learn model and calculates threat severity dynamically.
- **Zero-Config Demo Mode:** A seamless wrapper script sets up the environment and installs dependencies automatically.

---

## 🚀 How to Run (Demo Mode)

The easiest way to launch the application is by using the root entry script, which automatically checks for missing dependencies, configures the environment, and launches the server.

1. Navigate into the project directory:
   ```bash
   cd ml_cybersecurity
   ```

2. Run the Demo Wrapper script:
   ```bash
   python3 app.py
   ```

3. Open **http://127.0.0.1:8000** in your browser.

---

## 🔐 Authentication

The dashboard is protected. For the Demo Mode, we are using the public OpenLDAP testing server (`ldap.forumsys.com`).

Use the following credentials to access the Network Admin Dashboard:
- **Username:** `tesla`
- **Password:** `password`

*(Other valid usernames include `einstein`, `euler`, and `galileo`.)*

---

## 📊 Dataset

The original dataset is too large to be stored in this repository.
Download it from:
👉 [https://cicresearch.ca/CICDataset/CIC-IDS-2017/](https://cicresearch.ca/CICDataset/CIC-IDS-2017/)