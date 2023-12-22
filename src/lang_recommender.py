import os
import csv
import openai
import tiktoken
import pandas as pd

from datetime import date

from langchain.vectorstores import Chroma
from langchain.vectorstores import FAISS
from langchain.embeddings import FakeEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings


today = date.today().strftime("%Y-%m-%d")


def data_processing(data_dir="src/data/synopsis"):
    data = pd.read_csv(f"{data_dir}/{today}.csv")
    data["description"] = data.apply(
        lambda row: f"Synopsis Description: {row.get('description', '').strip()}. Applicant Eligibility Description: {row.get('applicant_eligibilty_desc', '').strip()}. Applicant Types: {row.get('applicant_types', '').strip()}",
        axis=1,
    )

    # Define the headers for the output CSV file
    headers = ["opportunity_id", "description"]

    outfile = f"{data_dir}/{today}-combined.csv"
    with open(outfile, "w", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=headers)

        writer.writeheader()

        for _, row in data.iterrows():
            row = row.to_dict()
            # Extract the desired fields from each row
            output_row = {
                "opportunity_id": row["opportunity_id"],
                "description": row["description"].strip(),
            }

            # Write the extracted fields to the output file
            writer.writerow(output_row)
    return f"{data_dir}/{today}-combined.csv"


def get_documents(csv_path):
    loader = CSVLoader(file_path=csv_path)
    data = loader.load()

    # data transformers
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    return text_splitter.split_documents(data)


def text_embedding(
    docs, openapi_key=None, data_dir="src/data/", provider="huggingface"
):
    if provider == "huggingface":
        embedding_function = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
    elif provider == "openai":
        if openapi_key is None:
            raise
        embedding_function = OpenAIEmbeddings(openai_openapi_key=openapi_key)
    else:
        embedding_function = FakeEmbeddings(size=1352)

    today_db_file = os.path.join(data_dir, f"{today}_db")

    if os.path.exists(today_db_file):
        db = FAISS.load_local(today_db_file, embedding_function)
    else:
        db = FAISS.from_documents(docs, embedding_function)
        db.save_local(today_db_file)
    return db


def get_similarity_docs(db, texts):
    docs = db.similarity_search(texts)
    return docs


if __name__ == "__main__":
    business_description = """
Financial Information:

Annual Revenue: $2.5 million (as of last fiscal year)
Expenses: $1.8 million (including operational costs, R&D, and marketing)
Funding Requirements: Seeking $500,000 in funding to expand product development and market reach.
Current Funding Sources: No outstanding loans or external funding.
Project or Initiative Details:
We aim to develop a new software platform that integrates AI-driven analytics to optimize workflow efficiency for small and medium-sized enterprises (SMEs). The funds will primarily support R&D, hiring additional software engineers, and marketing efforts. The project is estimated to take 18 months from development to launch.

Budget Breakdown:

Research & Development: $250,000
Hiring & Training: $150,000
Marketing & Promotion: $80,000
Contingency: $20,000
Legal and Compliance Information:

Registered LLC in the State of XYZ (LLC Registration Number: 12345-ABC)
All necessary business licenses and permits are up-to-date and compliant with state regulations.
Employee Information:

Current Staff: 20 employees (10 developers, 5 marketers, 5 administrative staff)
Highly skilled team with expertise in software development, machine learning, and project management.
Community Impact:
ABC Tech Solutions actively participates in local tech meetups, mentors students in coding boot camps, and sponsors technology education programs for underprivileged youth.

Previous Grants or Funding Received:
No previous grants or external funding received; self-funded since inception in 2018.
    """

    outputfile = data_processing()
    docs = get_documents(outputfile)
    db = text_embedding(docs)
    similarity_docs = get_similarity_docs(db, business_description)
    import pprint

    for doc in similarity_docs:
        print()
        print(doc.page_content)
