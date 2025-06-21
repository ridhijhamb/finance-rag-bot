import os
import requests
import re
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Ridhi Jhamb - MLE - ridhi@example.com"  
}

def get_filing_url(cik: str, form_type="10-K"):
    cik = cik.zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    data = res.json()
    for filing in data["filings"]["recent"]["form"]:
        if filing == form_type:
            index = data["filings"]["recent"]["form"].index(filing)
            accession = data["filings"]["recent"]["accessionNumber"][index].replace("-", "")
            return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{accession}-index.html"
    return None

def get_latest_10k_filing_url(cik):
    cik = cik.zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    data = res.json()

    forms = data["filings"]["recent"]["form"]
    accession_numbers = data["filings"]["recent"]["accessionNumber"]
    primary_docs = data["filings"]["recent"]["primaryDocument"]

    for i, form_type in enumerate(forms):
        if form_type == "10-K":
            acc_num = accession_numbers[i].replace("-", "")
            doc_name = primary_docs[i]
            
            # Skip XML/XBRL docs
            if doc_name.endswith(".htm") or doc_name.endswith(".html") or doc_name.endswith(".txt"):
                return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_num}/{doc_name}"
    
    return None



# def extract_filing_text(index_url):
#     res = requests.get(index_url, headers=HEADERS)
#     soup = BeautifulSoup(res.text, "html.parser")

#     # Find the table with filing documents
#     table = soup.find("table", class_="tableFile")
#     if not table:
#         print("Filing table not found on page.")
#         return ""

#     filing_link = None
#     for row in table.find_all("tr"):
#         cols = row.find_all("td")
#         if len(cols) >= 4 and ("10-K" in cols[3].text or "Complete submission text file" in cols[1].text):
#             try:
#                 filing_link = cols[2].a["href"]
#                 break
#             except Exception as e:
#                 print(f"Error extracting link: {e}")

#     if not filing_link:
#         print("No 10-K document link found in filing table.")
#         return ""

#     full_url = f"https://www.sec.gov{filing_link}"
#     print(f"Downloading full filing from: {full_url}")
#     doc = requests.get(full_url, headers=HEADERS).text
#     text = BeautifulSoup(doc, "lxml").get_text()
#     return clean_text(text)

def extract_filing_text(filing_url):
    print(f"Downloading full filing from: {filing_url}")
    doc = requests.get(filing_url, headers=HEADERS).text
    text = BeautifulSoup(doc, "lxml").get_text()
    return clean_text(text)


import re

def clean_text(text):
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove weird XBRL tags (e.g. us-gaap:, iso4217:, etc.)
    text = re.sub(r"\b[a-zA-Z0-9\-_:]{3,}:[a-zA-Z0-9\-_:]+", "", text)

    # Remove URLs
    text = re.sub(r"http[s]?://\S+", "", text)

    # Collapse redundant punctuation
    text = re.sub(r"[.]{2,}", ".", text)

    # Keep only reasonable characters
    text = re.sub(r"[^a-zA-Z0-9.,:;()\- \n]", "", text)

    return text.strip()


def save_to_file(text, company_name):
    os.makedirs("data/edgar_sec_filings", exist_ok=True)
    with open(f"data/edgar_sec_filings/{company_name}_10K.txt", "w", encoding="utf-8") as f:
        f.write(text)

if __name__ == "__main__":
    companies = {
        "apple": "0000320193",
        "amazon": "0001018724"
    }

    for name, cik in companies.items():
        print(f"Processing {name}")
        filing_url = get_latest_10k_filing_url(cik)
        print(f"Filing URL: {filing_url}")
        if filing_url:
            text = extract_filing_text(filing_url)
            save_to_file(text, name)
        else:
            print(f"No 10-K found for {name}")
