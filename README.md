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

- Python 3.6+

### Installation

Install via PyPI:

```bash
pip install baseline-checker
```
Install via npm :
```bash
npm i -g baseline-checker
```

Or clone the repository:

```bash
git clone https://github.com/Veeresh-Hanni/baseline-checker.git
cd baseline-checker
```

Create a virtual environment and install dependencies:

```bash
python -m venv venv
# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

---

### Usage

Run the scanner from the command line, providing the path to your project:

```bash
baseline-checker /path/to/your/project
```

#### Generate Specific Reports

- **JSON report**

```bash
baseline-checker /path/to/your/project --json
```

- **CSV report**

```bash
baseline-checker /path/to/your/project --csv
```

- **Word (DOCX) report**

```bash
baseline-checker /path/to/your/project --docx
```

- **PDF report**

```bash
baseline-checker /path/to/your/project --pdf
```

- **All reports at once**

```bash
baseline-checker /path/to/your/project --json --csv --docx --pdf
```

---

## 🛠️ Built With

- **Python** – Core scanning engine and reporting tools
- **Pandas** – Data manipulation and CSV report generation
- **python-docx** – Word document reports
- **ReportLab** & **FPDF**– PDF generation
- **Rich** – Beautiful console output
- **Colorama** - Colorfull console
- **tqdm** – Progress bars

---

## 🤝 Contributing

Contributions are welcome! Open an issue or submit a pull request.
