# AI-Powered Web Scraper

## English Version

This project is an intelligent web crawler that recursively navigates websites using Selenium and Ollama AI models to produce prioritized articles.

### Key Features

- Automated website crawling with Selenium in headless mode
- Evaluation and prioritization of links using AI
- Generation of summarized articles with a professional tone
- Fully configurable through external files

## Prerequisites

- Python 3.8+
- Firefox Browser
- Ollama with at least one LLM model installed 

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

### Configuration Files Manual

#### 1. `websites.txt`
- **Description**: This file should contain the main URLs that you want the scraper to visit.
- **Format**: Each URL should be on a new line.
- **Example**:
  ```
  https://www.example.com
  https://www.anotherexample.com
  ```

#### 2. `topics.txt`
- **Description**: This file lists the topics of interest that the AI will use to evaluate content.
- **Format**: Each topic should be on a new line.
- **Example**:
  ```
  Artificial Intelligence
  Climate Change
  Technology
  ```

#### 3. `model_config.yaml`
- **Description**: This file contains settings for the AI models used in the scraper.
- **Format**: YAML format. Ensure proper indentation.
- **Example**:
  ```yaml
  models:
    content:
      name: "your_content_model_name"
    links:
      name: "your_links_model_name"
  prompts:
    link_evaluation: "Evaluate the link based on the following topics: {topics} for the URL: {url}"
    content_evaluation: "Evaluate the content based on the following topics: {topics} and content: {content}"
    article_generation: "Generate an article based on the following content: {content} and topics: {topics}"
  thresholds:
    link_score: 0.5  # Change this value to set the score threshold for link evaluation
  ```

#### 4. `exclusions.txt`
- **Description**: This file contains URLs that should be excluded from scraping.
- **Format**: Each URL should be on a new line.
- **Example**:
  ```
  https://www.example.com/excluded-page
  ```

#### 5. `limits.yaml`
- **Description**: This file sets limits for the scraping process, such as maximum depth and request delays.
- **Format**: YAML format. Ensure proper indentation.
- **Example**:
  ```yaml
  scraping:
    max_depth: 3
    request_delay: 2  # Delay in seconds between requests
    max_links_per_page: 10
  ```

## Usage

To run the program:
```bash
python src/main.py
```

Outputs will be saved in the `output` folder, including a summary HTML file that displays one article at a time with navigation buttons.

---

## نسخه فارسی

این پروژه یک خزنده وب هوشمند است که با استفاده از Selenium و مدل‌های هوش مصنوعی Ollama، به صورت بازگشتی وب‌سایت‌ها را پیمایش کرده و مقالات اولویت‌بندی شده تولید می‌کند.

### ویژگی‌های اصلی

- پیمایش خودکار وب‌سایت‌ها با Selenium در حالت headless
- ارزیابی و اولویت‌بندی لینک‌ها با استفاده از هوش مصنوعی
- تولید مقالات خلاصه‌شده با لحن حرفه‌ای
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

### راهنمای فایل‌های پیکربندی

#### 1. `websites.txt`
- **توضیحات**: این فایل باید شامل URLهای اصلی باشد که می‌خواهید خزنده به آن‌ها مراجعه کند.
- **فرمت**: هر URL باید در یک خط جدید باشد.
- **مثال**:
  ```
  https://www.example.com
  https://www.anotherexample.com
  ```

#### 2. `topics.txt`
- **توضیحات**: این فایل شامل موضوعات مورد علاقه است که هوش مصنوعی برای ارزیابی محتوا از آن‌ها استفاده می‌کند.
- **فرمت**: هر موضوع باید در یک خط جدید باشد.
- **مثال**:
  ```
  هوش مصنوعی
  تغییرات آب و هوا
  فناوری
  ```

#### 3. `model_config.yaml`
- **توضیحات**: این فایل شامل تنظیمات مدل‌های هوش مصنوعی مورد استفاده در خزنده است.
- **فرمت**: فرمت YAML. اطمینان حاصل کنید که فاصله‌گذاری به درستی انجام شده است.
- **مثال**:
  ```yaml
  models:
    content:
      name: "your_content_model_name"
    links:
      name: "your_links_model_name"
  prompts:
    link_evaluation: "Evaluate the link based on the following topics: {topics} for the URL: {url}"
    content_evaluation: "Evaluate the content based on the following topics: {topics} and content: {content}"
    article_generation: "Generate an article based on the following content: {content} and topics: {topics}"
  thresholds:
    link_score: 0.5  # این مقدار را برای تنظیم آستانه امتیاز ارزیابی لینک تغییر دهید
  ```

#### 4. `exclusions.txt`
- **توضیحات**: این فایل شامل URLهایی است که باید از خزیدن مستثنی شوند.
- **فرمت**: هر URL باید در یک خط جدید باشد.
- **مثال**:
  ```
  https://www.example.com/excluded-page
  ```

#### 5. `limits.yaml`
- **توضیحات**: این فایل محدودیت‌هایی برای فرآیند خزیدن، مانند حداکثر عمق و تأخیر درخواست‌ها را تنظیم می‌کند.
- **فرمت**: فرمت YAML. اطمینان حاصل کنید که فاصله‌گذاری به درستی انجام شده است.
- **مثال**:
  ```yaml
  scraping:
    max_depth: 3
    request_delay: 2  # تأخیر به ثانیه بین درخواست‌ها
    max_links_per_page: 10
  ```

## استفاده

برای اجرای برنامه:
```bash
python src/main.py
```

خروجی‌ها در پوشه `output` ذخیره خواهند شد، از جمله یک فایل HTML خلاصه که یک مقاله را در هر بار نمایش می‌دهد و دارای دکمه‌های ناوبری است. 