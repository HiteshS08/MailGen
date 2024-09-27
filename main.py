import streamlit as st
import logging
from chain import Chain
from portfolio import Portfolio
from utils import scrape_and_clean_text

logging.basicConfig(level=logging.INFO)


def create_streamlit_app(new_chain, new_portfolio):
    st.title("📧 Cold Mail Generator")
    url_input = st.text_input("Enter a Careers Page URL:", value="https://jobs.nike.com/job/R-33460")
    submit_button = st.button("Generate Email")

    if submit_button:
        with st.spinner("Processing..."):
            try:
                cleaned_text = scrape_and_clean_text(url_input)
                if not cleaned_text:
                    st.error("Failed to retrieve content from the URL.")
                    return

                jobs = new_chain.extract_jobs(cleaned_text)
                if not jobs:
                    st.error("No job postings found on the provided URL.")
                    return

                for idx, job in enumerate(jobs):
                    st.subheader(f"Job Posting {idx + 1}: {job.get('role', 'Unknown Role')}")
                    job_description = f"{job.get('description', '')} Skills required: {', '.join(job.get('skills', []))}"
                    links = new_portfolio.get_relevant_portfolio_links(job_description)
                    email = new_chain.write_mail(job, links)

                    st.markdown("### Generated Email:")
                    st.code(email, language='markdown')
            except Exception as e:
                logging.error(f"An error occurred: {e}")
                st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(
        layout="wide",
        page_title="Cold Email Generator",
        page_icon="📧"
    )
    create_streamlit_app(chain, portfolio)
