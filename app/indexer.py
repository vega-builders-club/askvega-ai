import requests
import logging
import pickle
import tempfile
import time
import re

from typing import List
from collections import deque
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from unstructured.partition.html import partition_html
from unstructured.partition.pdf import partition_pdf
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS

logger = logging.getLogger(__file__)

# RegEx domain urls to match
HTTP_URL_PATTERN = r'^http[s]{0,1}://.+$'

# RegEx for valid Vega blog post
BLOG_REGEX = r'^http[s]{0,1}:\/\/blog\.vega\.xyz\/[a-z0-9-]+-[a-f0-9]{12}$'


# Domain list to crawl
domain_whitelist = [
    "https://vega.xyz",
    "https://blog.vega.xyz",
    "https://docs.vega.xyz"
]


class Indexer(BaseLoader):
    def __init__(self, domains: List[str],
                 continue_on_failure: bool = True,
                 ):
        # Temp documents of extracted contents
        self.docs: List[Document] = list()

        # Set to True to ignore any failed URL request
        self.continue_on_failure = continue_on_failure

        # A list of domains to crawl
        self.domains = domains

        # create a queue of nested urls in a webpage
        self.queue = deque([domains[0]])

        # create a queue of urls crawled already
        self.seen = set([domains[0]])

        # Initialize selenium chrome driver
        service = ChromeService(ChromeDriverManager().install())

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")

        self.driver = webdriver.Chrome(
            service=service, options=chrome_options)

    def get_and_ingest_pdf(self, url: str):

        download = requests.get(url, stream=True)

        if download.status_code != 200:
            raise ValueError("Failed to download PDF file %s" %
                             download.status_code)

        self.temp_file = tempfile.NamedTemporaryFile()
        self.temp_file.write(download.content)
        elements = partition_pdf(
            filename=self.temp_file.name, strategy="fast")

        return elements

    def is_valid_url(self, url: str) -> bool:
        try:
            response = urlparse(url)
            return all([response.scheme, response.netloc])
        except ValueError:
            return False

    def scroll_if_blog_home(self):
        view_height = self.driver.execute_script(
            "return document.body.scrollHeight")

        while True:
            # Scroll to bottom of page to load more contents
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            # Allow some time for content to load
            print("Waiting 5 seconds for contents to load...")
            time.sleep(5)

            # Get new view height
            new_view_height = self.driver.execute_script(
                "return document.body.scrollHeight")

            # Check if view height changed
            if view_height == new_view_height:
                break

            view_height = new_view_height

    def get_urls_from_page(self, soup: BeautifulSoup, domain: str) -> List[str]:
        links = []

        for a in soup.find_all("a"):
            link = a.get("href")
            # Clean URL from source query params if any
            if link is not None:
                clean_link = link.split("?source=")[0]
                if clean_link.startswith("/"):
                    clean_link = domain + "/" + link[1:]
                    links.append(clean_link)
                else:
                    links.append(clean_link)

        return links

    def clean_and_save_urls(self, links: List[str]) -> None:
        for link in links:
            # Strip trailing slash
            link = link.strip("/")
            parsed_url = urlparse(link)
            full_url = parsed_url.scheme + "://" + parsed_url.netloc

            # Check if the base url matches any of our whitelisted domains
            if link not in self.seen and full_url in self.domains:
                # Ensure only clean blog urls are added to the queue
                if full_url == "https://blog.vega.xyz":
                    if re.match(BLOG_REGEX, link):
                        self.queue.append(link)
                        self.seen.add(link)
                else:
                    self.queue.append(link)
                    self.seen.add(link)

    def load(self) -> List[Document]:

        for domain in self.domains:

            while self.queue:
                # get the next url to crawl from the queue
                url = self.queue.pop()
                try:
                    print("Indexing: " + url)

                    if url.endswith(".pdf"):
                        elements = self.get_and_ingest_pdf(url)

                        # Blank to avoid soup from throwing
                        soup = BeautifulSoup("", "html.parser")
                        self.temp_file.close()

                    else:
                        self.driver.get(url)

                        if url == "https://blog.vega.xyz":
                            self.scroll_if_blog_home()

                        webpage = self.driver.page_source
                        soup = BeautifulSoup(webpage, "html.parser")
                        elements = partition_html(text=webpage)

                except Exception as e:
                    if self.continue_on_failure:
                        logger.error(
                            f"Error indexing {url}, exeption: {e}")
                    else:
                        raise e

                # Clean HTML and flatten to string
                text = "\n\n".join([str(el) for el in elements])
                metadata = {"source": url}
                self.docs.append(
                    Document(page_content=text, metadata=metadata))

                # Find all nested urls
                links = self.get_urls_from_page(soup, domain)

                # Check to see if the link has been crawled before and skip
                self.clean_and_save_urls(links)

        self.driver.quit()
        return self.docs


def index_domains():
    # Start indexing
    indexer = Indexer(domains=domain_whitelist)
    raw_documents = indexer.load()

    # Chunk documents to fit OpenAi spec
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200)
    documents = text_splitter.split_documents(raw_documents)

    # Create embeddings and store in a vector store
    embeddings = OpenAIEmbeddings()
    vectorstor = FAISS.from_documents(documents, embeddings)

    # save vectorstor
    with open("askvega.pk1", "wb") as f:
        pickle.dump(vectorstor, f)


if __name__ == "__main__":
    index_domains()
