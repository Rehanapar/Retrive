from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_google_genai import GoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate

from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank
from langchain.retrievers import ContextualCompressionRetriever
import numpy as np
from langchain_community.document_loaders import PyPDFLoader


from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

connection_string = 'mongodb+srv://hbanu130:3u1NEcAf7AWsmRlq@cluster0.heta0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient

# initialize MongoDB python client
client = MongoClient("mongodb+srv://hbanu130:3u1NEcAf7AWsmRlq@cluster0.heta0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

DB_NAME = "Employee"
COLLECTION_NAME = "Customer"

ATLAS_VECTOR_SEARCH_INDEX_NAME = "vector_index"

MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]

loader = PyPDFLoader("A_Retrieval-Augmented_Generation_Based_Large_Langu.pdf")
docs = loader.load()
from langchain_community.embeddings import HuggingFaceEmbeddings

# # Initialize Hugging Face embeddings using a specific model
embeddings = HuggingFaceEmbeddings(model_name="bert-base-uncased")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True
)
all_splits = text_splitter.split_documents(docs)

vector_store = MongoDBAtlasVectorSearch(
    collection = MONGODB_COLLECTION,
    embedding=embeddings,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    relevance_score_fn="cosine",
)

from uuid import uuid4

uuids = [str(uuid4()) for _ in range(len(docs))]

vector_store.add_documents(documents=docs, ids=uuids)

import google.generativeai as genai
genai.configure(api_key='AIzaSyB8Aebx65teGmAkVaLuYvVrJuNM5oc2lvg')
llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key='AIzaSyB8Aebx65teGmAkVaLuYvVrJuNM5oc2lvg')


# Define prompt template
template = """Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Use three sentences maximum and keep the answer as concise as possible.
Always say "thanks for asking!" at the end of the answer.
{context} Question: {question} Helpful Answer:"""

prompt = ChatPromptTemplate.from_template(template)

# Initialize retriever
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 6})

def format_docs(texts):
    return "\n\n".join(doc.page_content for doc in texts)

# RAG Chain
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt | llm | StrOutputParser()
)


# Invoke RAG chain with a question
response = rag_chain.invoke("What is Retrieval?")
print(response)