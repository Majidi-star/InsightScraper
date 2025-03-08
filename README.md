# AI-Powered Web Scraper

## English Version

This project is an intelligent web crawler that recursively navigates websites using Selenium and Ollama AI models to produce prioritized articles.

### Key Features

- Automated website crawling with Selenium in headless mode
- Evaluation and prioritization of links using AI
- Generation of summarized articles with a professional tone
- Intelligent selection of relevant images
- Fully configurable through external files

## Prerequisites

- Python 3.8+
- Firefox Browser
- Ollama with the following models installed:
  - qwen2.5:latest
  - llava-llama3:latest

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Firefox and geckodriver are installed.

3. Configure the settings files in the `config` folder:
   - `websites.txt`: List of main URLs
   - `topics.txt`: Topics of interest
   - `model_config.yaml`: AI model settings
   - `exclusions.txt`: Excluded URLs
   - `limits.yaml`: Scraping limits

## Usage

To run the program:
```bash
python src/main.py
```

Outputs will be saved in the `output` folder.

---

## نسخه فارسی

این پروژه یک خزنده وب هوشمند است که با استفاده از Selenium و مدل‌های هوش مصنوعی Ollama، به صورت بازگشتی وب‌سایت‌ها را پیمایش کرده و مقالات اولویت‌بندی شده تولید می‌کند.

### ویژگی‌های اصلی

- پیمایش خودکار وب‌سایت‌ها با Selenium در حالت headless
- ارزیابی و اولویت‌بندی لینک‌ها با استفاده از هوش مصنوعی
- تولید مقالات خلاصه‌شده با لحن حرفه‌ای
- انتخاب هوشمند تصاویر مرتبط
- قابلیت پیکربندی کامل از طریق فایل‌های خارجی

## پیش‌نیازها

- Python 3.8+
- Firefox Browser
- Ollama با مدل‌های زیر نصب شده:
  - qwen2.5:latest
  - llava-llama3:latest

## نصب

1. نصب وابستگی‌ها:
   ```bash
   pip install -r requirements.txt
   ```

2. اطمینان از نصب Firefox و geckodriver.

3. پیکربندی فایل‌های تنظیمات در پوشه `config`:
   - `websites.txt`: لیست URL‌های اصلی
   - `topics.txt`: موضوعات مورد علاقه
   - `model_config.yaml`: تنظیمات مدل‌های هوش مصنوعی
   - `exclusions.txt`: URL‌های مستثنی شده
   - `limits.yaml`: محدودیت‌های پیمایش

## استفاده

برای اجرای برنامه:
```bash
python src/main.py
```

خروجی‌ها در پوشه `output` ذخیره خواهند شد. 