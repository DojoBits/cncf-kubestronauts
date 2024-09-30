# Kubestronaut Metrics: Top Countries Rankings

Blog post: [Kubestronaut Metrics: Top Countries Rankings](https://dojobits.io/blog/kubestronaut-metrics-top-countries-and-ranking/)

<p align="center">
  <img src="./img/kubestronaut.png" width="200" height="200">

## What the script does

Here's a high-level explanation of the script:

- **Environment Setup:** Loads credentials for Google Sheets and defines variables for accessing a specific Google Sheet.
- **Web Scraping with Selenium:** Scrapes Kubestronaut data from a website (CNCF's Kubestronaut page), extracting information about regions and countries and counting the number of Kubestronauts.
- **Asynchronous API Fetching:** Uses `aiohttp` to asynchronously retrieve population data for each country from the REST Countries API.
- **Data Preparation:** Combines scraped data with fetched population data and sorts it by the number of Kubestronauts.
- **Batch the Google Sheets Update:** Batch updates the Google Sheet to avoid Google API rate limits and ensure the sheet is updated efficiently.
- **Google Sheets Update:** Batch updates the Google Sheet with the Kubestronauts data and population information, ensuring the sheet is updated efficiently.


### 1. **Create a Virtual Environment**

Here’s how to set up the environment on both Linux and MacOS

First, create and activate a virtual environment to keep dependencies isolated.

```bash
~$ python3 -m venv myenv
~$ source myenv/bin/activate
```

### 2. **Install Required Packages**

In the repo you can find the requirements.txt file and use it basically we use just 3 packages `aiohttp`, `gspread` and `selenium`

```bash
pip install -r requirements.txt
```

### 3. **Install WebDriver for Selenium**

**For MacOS:**
 Use `Homebrew` to install `ChromeDriver`

 ```bash
 brew install chromedriver
 ```

**For Linux:**
 You can install ChromeDriver manually or through a package manager, depending on your distribution.

 **For Ubuntu/Debian:**
 ```bash
 sudo apt-get install chromium-chromedriver
 ```
 Ensure the `chromedriver` executable is in your system's PATH, or specify its location when initializing the Selenium WebDriver.

### 4. **Prepare Google Sheets API Credentials**

Set up your **Google Cloud project**, enable the **Google Sheets API**, and create a **Service Account**. You can follow the [gspread official doc](https://docs.gspread.org/en/latest/oauth2.html). When you are done you can download the service account credentials JSON file.

Best way is to use secret manager but for simplicity we will use it in env variable.

- GSHEET_CREDS is the JSON content of the service account credentials file
- GSHEET_KEY is the Google Sheet ID it looks something like "1BxiMVs0A5nFMdKvBdBZjptlbs74OgvE2upms"

 ```bash
 export GSHEET_CREDS="JSON content {...}"
 export GSHEET_KEY="CHANGE-THAT-1BxiMVs0A5nFMdKvtlbs74OgvE2upms"
 ```

If you decide to put it in your shell Reload the shell configuration to apply the changes:

 ```bash
 source ~/.bashrc  # or ~/.zshrc
 ```

### 5. **Run the Script**

Ensure the virtual environment is active and run your Python script:

<details>

<summary>Run the script</summary>

```bash
$ python3 kubestronauts.py
Starting Selenium to scrape Kubestronaut data...
Scraped 5 regions and 79 countries.
Fetching populations asynchronously...
Starting population fetch for all countries...
...
...
```
</details>
