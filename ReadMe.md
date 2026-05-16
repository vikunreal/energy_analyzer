content = """# ⚡ Energy Bill Data Analyzer

A lightweight, containerized Python application built with **Streamlit** and **Pandas** to help you analyze your energy consumption and estimate your bills. By uploading your smart meter's CSV export and entering your tariff details, you can see exactly where your money is going.

---

## ✨ Features

- **📂 CSV Upload:** Supports various smart meter export formats with dynamic column detection (looks for timestamps and consumption values).
- **💰 Flexible Tariffs:**
    - **Flat Rate:** One price for all hours.
    - **Dual-Rate (Peak/Off-Peak):** Custom off-peak windows (e.g., Economy 7, EV tariffs like Octopus Go).
- **🗓️ Standing Charge Calculation:** Automatically calculates total standing charges based on the date range in your data.
- **📊 Visual Insights:**
    - Daily consumption bar charts.
    - Cost breakdown (Standing charge vs. Usage).
    - Summary metrics (Total kWh, Total Cost).
- **🐳 Dockerized:** Ready to run in a single command on your home server or local machine.

---

## 🚀 Quick Start

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Installation

1. **Clone or Copy the Files:**
   Ensure you have the following files in your project directory:
   - `app.py`
   - `requirements.txt`
   - `Dockerfile`
   - `docker-compose.yml`

2. **Launch the Application:**
   Run the following command in your terminal:
   ```bash
   docker compose up -d --build