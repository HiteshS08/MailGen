import os
import logging
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document

load_dotenv()
logging.basicConfig(level=logging.INFO)


class Chain:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.1-70b-versatile"
        )

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """### SCRAPED TEXT FROM WEBSITE: {page_data} ### INSTRUCTION: The scraped text is from the careers page 
            of a website. Your job is to extract the job postings and return them in JSON format containing the 
            following keys: role, experience, skills, and description. Only return the valid JSON. ### VALID JSON (NO 
            PREAMBLE):"""
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
            logging.info("Successfully extracted job postings.")
        except OutputParserException as e:
            logging.error(f"Error parsing job postings: {e}")
            raise OutputParserException("Unable to parse job postings.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION: You are John, a business development executive at AtliQ. AtliQ is an AI & Software Consulting 
            company dedicated to facilitating the seamless integration of business processes through automated tools. 
            Over our experience, we have empowered numerous enterprises with tailored solutions, fostering 
            scalability, process optimization, cost reduction, and heightened overall efficiency. Your job is to 
            write a cold email to the client regarding the job mentioned above describing the capability of AtliQ in 
            fulfilling their needs. Also add the most relevant ones from the following links to showcase AtliQ's 
            portfolio: {link_list} Remember you are John, BDE at AtliQ. Do not provide a preamble. ### EMAIL (NO 
            PREAMBLE):"""
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({
            "job_description": job,
            "link_list": ', '.join(links)
        })
        logging.info("Successfully generated the cold email.")
        return res.content
