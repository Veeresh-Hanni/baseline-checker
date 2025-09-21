# Baseline Checker: A Modern Web Compatibility Scanner

![Baseline Checker](https://placehold.co/600x300/2a2d34/ffffff?text=Baseline+Checker)

**Baseline Checker** is a powerful command-line tool that scans your web projects to identify the use of modern vs. non-baseline web features. It helps you ensure your codebase is modern, maintainable, and compatible across the majority of browsers, aligning with [Google&#39;s Baseline initiative](https://web.dev/baseline).

---

## The Problem

In today's fast-evolving web landscape, it's a challenge for developers to know if they are using the most modern, widely-supported browser features. Manually checking a large codebase for hundreds of APIs, CSS properties, and JavaScript features is tedious and prone to error.

## The Solution

Our **Baseline Checker** automates this process. It's a Python-based tool that recursively scans a project directory, intelligently filters out irrelevant files (like `node_modules`), and analyzes your code to generate a comprehensive compatibility report.

This empowers developers to:

* ✅ **Verify** that their code is modern and future-proof.
* 🧐 **Identify** legacy or experimental features that might cause cross-browser compatibility issues.
* 📚 **Learn** which modern APIs they can adopt to replace older techniques.
* 📄 **Generate** shareable reports in multiple formats (JSON, CSV, DOCX, and PDF) to easily communicate the project's technical status.

---

## ✨ Features

* **Comprehensive Scanning:** Recursively scans entire project directories.
* **Intelligent Filtering:** Skips common irrelevant folders (`node_modules`, `.git`, `dist`, etc.) for faster, more relevant scans.
* **Data-Driven:** Uses a detailed JSON file (`baseline_data.json`) containing hundreds of web features and their Baseline status, making it easily updatable.
* **Multi-Format Reporting:** Generates clean, professional reports in JSON, CSV, DOCX, and PDF formats.
* **User-Friendly CLI:** Provides clear console output with progress bars (`tqdm`) and formatted text (`rich`) for a great user experience.
* **Resilient:** Gracefully handles file access errors and allows for graceful interruption (`Ctrl+C`) with an option to save a partial report.

---

## 🚀 Getting Started

### Prerequisites

* Python 3.6+

### Installation

1. **Clone the repository:**

   ```sh
   git clone [https://github.com/your-username/baseline-checker.git](https://github.com/your-username/baseline-checker.git)
   cd baseline-checker
   ```
2. **Install the dependencies:**
   It's recommended to use a virtual environment.

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

### Usage

Run the scanner from the command line, providing the path to the project you want to analyze. You can also specify which reports you want to generate.

**Basic Scan:**

```sh
python baseline_checker.py /path/to/your/project
```

**Generate Specific Reports:**
Use flags to generate reports. The reports will be saved in the root of the `baseline-checker` directory.

```sh
# Generate a JSON report
python baseline_checker.py /path/to/your/project --json

# Generate a CSV report
python baseline_checker.py /path/to/your/project --csv

# Generate a Word (DOCX) report
python baseline_checker.py /path/to/your/project --docx

# Generate a PDF report
python baseline_checker.py /path/to/your/project --pdf

# Generate all reports at once
python baseline_checker.py /path/to/your/project --json --csv --docx --pdf
```

---

## 🛠️ Built With

* **Python:** The core language for the scanning engine and reporting tools.
* **Pandas:** Used for data manipulation and generating the CSV report.
* **python-docx:** To create the professional Word document report.
* **ReportLab:** For generating the clean and portable PDF report.
* **Rich:** To provide beautiful and informative console output.
* **tqdm:** Powers the user-friendly progress bars during the scan.

---
