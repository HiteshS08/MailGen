import logging
import requests
from bs4 import BeautifulSoup
import re


def scrape_and_clean_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        logging.info(f"Successfully fetched data from {url}")
    except requests.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return ""

    soup = BeautifulSoup(response.text, 'html.parser')
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()
    text = soup.get_text(separator=' ')
    cleaned_text = clean_text(text)
    return cleaned_text


def clean_text(text):
    text = re.sub(r'&[^;\s]+;', '', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text
