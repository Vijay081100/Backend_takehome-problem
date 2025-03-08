import test2.py
[tool.poetry.dependencies]
requests = "^2.25.1"
pandas = "^1.3.3"
import requests
import pandas as pd
import re
from typing import List, Dict

class PubMedFetcher:
    def __init__(self, query: str):
        self.query = query
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.detail_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    
    def fetch_paper_ids(self) -> List[str]:
        params = {
            "db": "pubmed",
            "term": self.query,
            "retmode": "json",
            "retmax": "20"
        }
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data["esearchresult"]["idlist"]
    
    def fetch_paper_details(self, ids: List[str]) -> List[Dict[str, str]]:
        params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "json"
        }
        response = requests.get(self.detail_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data["result"]
    
    def parse_authors(self, authors: List[Dict]) -> (List[str], List[str]):
        non_academic_authors = []
        company_affiliations = []
        for author in authors:
            affiliation = author.get("affiliation", "")
            if affiliation and not re.search(r"(university|lab|institute)", affiliation, re.IGNORECASE):
                non_academic_authors.append(author["name"])
                company_affiliations.append(affiliation)
        return non_academic_authors, company_affiliations
    
    def fetch_and_filter_papers(self) -> pd.DataFrame:
        paper_ids = self.fetch_paper_ids()
        papers = self.fetch_paper_details(paper_ids)
        
        records = []
        for paper in papers.values():
            if paper == {}:
                continue
            authors, affiliations = self.parse_authors(paper.get("authors", []))
            if authors:
                records.append({
                    "PubmedID": paper["uid"],
                    "Title": paper["title"],
                    "Publication Date": paper["pubdate"],
                    "Non-academic Author(s)": "; ".join(authors),
                    "Company Affiliation(s)": "; ".join(affiliations),
                    "Corresponding Author Email": paper.get("authorList", [{}])[0].get("email", "N/A")
                })
        
        return pd.DataFrame(records)

def save_to_csv(df: pd.DataFrame, filename: str):
    df.to_csv(filename, index=False)
