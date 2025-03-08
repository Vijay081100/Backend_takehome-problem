import argparse
import logging
import fetch_papers

def main():
    parser = argparse.ArgumentParser(description="Fetch research papers based on a query.")
    parser.add_argument("query", type=str, help="The search query for fetching papers.")
    parser.add_argument("-f", "--file", type=str, help="The filename to save results as CSV.")
    parser.add_argument("-d", "--debug", action="store_true", help="Print debug information.")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    
    fetcher = fetch_papers.PubMedFetcher(args.query)
    papers_df = fetcher.fetch_and_filter_papers()
    
    if args.file:
        fetch_papers.save_to_csv(papers_df, args.file)
    else:
        print(papers_df)

if __name__ == "__main__":
    main()
[tool.poetry.scripts]
get-papers-list = "main:main"
