import logging
import os
import pandas as pd
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document


class Portfolio:
    def __init__(self, file_path="resources/my_portfolio.csv"):
        self.file_path = file_path
        self.data = pd.read_csv(self.file_path)
        self.embeddings = HuggingFaceEmbeddings()
        self.vector_store = None
        self.setup_portfolio_vector_store()

    def setup_portfolio_vector_store(self):
        if self.data.empty:
            logging.error("Portfolio CSV is empty or not found.")
            return

        documents = []
        for _, row in self.data.iterrows():
            content = row.get('TechStack', '')
            metadata = {'link': row.get('Links', '')}
            documents.append(Document(page_content=content, metadata=metadata))

        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        logging.info(f"Portfolio vector store initialized with {len(documents)} items.")

    def get_relevant_portfolio_links(self, job_description, top_k=3):
        if not self.vector_store:
            logging.error("Vector store is not initialized.")
            return []

        similar_docs = self.vector_store.similarity_search(job_description, k=top_k)
        links = [doc.metadata['link'] for doc in similar_docs if doc.metadata.get('link')]
        logging.info(f"Retrieved {len(links)} relevant portfolio links.")
        return links
