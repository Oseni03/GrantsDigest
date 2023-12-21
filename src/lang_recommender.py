import os
import csv
import openai
import tiktoken
import pandas as pd

from datetime import date
from openai.embeddings_utils import get_embedding

from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings import FakeEmbeddings
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings


today = date.today().strftime("%Y-%m-%d")


def data_processing(data_dir="src/data/synopsis"):
    data = pd.read_csv(f"{data_dir}/{today}.csv")
    data["description"] = data.apply(
        lambda row: f"Synopsis Description: {row['description']}. Applicant Eligibility Description: {row['applicant_eligibilty_desc']}. Applicant Types: {row['applicant_types']}",
        axis=1,
    )

    # Define the headers for the output CSV file
    headers = ["opportunity_id", "description"]

    outfile = f"{data_dir}/{today}-combined.csv"
    with open(outfile, "w", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=headers)

        writer.writeheader()

        for row in data:
            # Extract the desired fields from each row
            output_row = {
                "opportunity_id": row["opportunity_id"],
                "description": f"{row['description']}",
            }

            # Write the extracted fields to the output file
            writer.writerow(output_row)
    return outfile


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
        db = Chroma(
            persist_directory=today_db_file, embedding_function=embedding_function
        )
    else:
        db = Chroma.from_documents(
            docs, embedding_function, persist_directory=today_db_file
        )
    return db
