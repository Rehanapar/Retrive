from flask import Flask, request, jsonify
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank
from langchain.retrievers import ContextualCompressionRetriever
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient, TEXT
from uuid import uuid4
import google.generativeai as genai

from langchain_community.embeddings import HuggingFaceEmbeddings

app = Flask(__name__)

embeddings = HuggingFaceEmbeddings(model_name="bert-base-uncased")

# Load and preprocess PDFs
loader = PyPDFLoader("A_Retrieval-Augmented_Generation_Based_Large_Langu.pdf")
docs = loader.load()
# print(docs)

# MongoDB configuration
MONGODB_ATLAS_CLUSTER_URI = "mongodb+srv://hbanu130:3u1NEcAf7AWsmRlq@cluster0.heta0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "Employee"
COLLECTION_NAME = "Customer"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "vector_index"

# Initialize MongoDB client and collection
client = MongoClient(MONGODB_ATLAS_CLUSTER_URI)
MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]

 
# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True
)
all_splits = text_splitter.split_documents(docs)
 
# Initialize MongoDB Atlas Vector Search
vector_store = MongoDBAtlasVectorSearch(
    collection=MONGODB_COLLECTION,
    embedding=embeddings,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    relevance_score_fn="cosine"
)
 
# Add documents to vector store
uuids = [str(uuid4()) for _ in range(len(docs))]
vector_store.add_documents(documents=docs, ids=uuids)
 
# Set up Google Generative AI
import google.generativeai as genai
genai.configure(api_key='AIzaSyB8Aebx65teGmAkVaLuYvVrJuNM5oc2lvg')
llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key='AIzaSyB8Aebx65teGmAkVaLuYvVrJuNM5oc2lvg')
# Set up Google Generative AI
# import google.generativeai as genai
# genai.configure(api_key='AIzaSyB8Aebx65teGmAkVaLuYvVrJuNM5oc2lvg')
# llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key='AIzaSyB8Aebx65teGmAkVaLuYvVrJuNM5oc2lvg')
# Set up Google Generative AI
# genai.configure(api_key='AIzaSyB8Aebx65teGmAkVaLuYvVrJuNM5oc2lvg')  # Replace with your API key
# llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key='AIzaSyB8Aebx65teGmAkVaLuYvVrJuNM5oc2lvg')  # Replace with your API key
 
# Define prompt template
template = """Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Use three sentences maximum and keep the answer as concise as possible.
Always say "thanks for asking!" at the end of the answer.
{context} Question: {question} Helpful Answer:"""
 
prompt = ChatPromptTemplate.from_template(template)
 
# Initialize retriever
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 6})
 
# Function to format documents for input
def format_docs(texts):
    return "\n\n".join(doc.page_content for doc in texts)
 
# RAG Chain
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt | llm | StrOutputParser()
)


# # Ensure that only the page content is passed for embedding
# def format_docs_for_embedding(docs):
#     return [doc.page_content for doc in docs]  # Extract text content only

# # Function to ensure that the retrieved documents are formatted as strings (extracting the text)
# def format_docs_for_embedding(docs):
#     return [doc.page_content if isinstance(doc, dict) else doc for doc in docs]  # Handle dict or doc object

# # Function to extract text from documents or handle dicts properly
# def format_docs_for_embedding(docs):
#     formatted_docs = []
#     for doc in docs:
#         if isinstance(doc, dict):
#             # Extract 'page_content' or equivalent from the dict if it exists
#             if 'page_content' in doc:
#                 formatted_docs.append(doc['page_content'])
#             else:
#                 formatted_docs.append(str(doc))  # Convert the dict to string as a fallback
#         else:
#             formatted_docs.append(doc)
#     return formatted_docs

# # Flask route with the fixed retrieval and formatting
# @app.route('/api/retrieve', methods=['POST'])
# def retrieve():
#     data = request.json
#     query = data.get("query")
#     if not query:
#         return jsonify({"error": "Query is required"}), 400
    
#     # Use the invoke method to get relevant documents
#     retrieved_docs = retriever.invoke({"query": query})

#     # Format the documents to ensure only text is passed to the embedding function
#     formatted_docs = format_docs_for_embedding(retrieved_docs)

#     # Use RAG chain to get a response
#     response = rag_chain.invoke({"context": formatted_docs, "question": query})

#     return jsonify({"response": response})




# @app.route('/api/retrieve', methods=['POST'])
# def retrieve():
#     data = request.json
#     query = data.get("query")
#     if not query:
#         return jsonify({"error": "Query is required"}), 400

#     # Use RAG chain to get response
#     response = rag_chain.invoke({"context": retriever.get_relevant_documents(query), "question": query})

#     return jsonify({"response": response})

@app.route('/api', methods=['POST'])
def retrieve():
    print("POST /ai called")
    data = request.json
    query = data.get("query", "")  # Get query safely
    print(f"Type of query: {type(query)}, value: {query}")

    if not isinstance(query, str):
        return jsonify({"error": "Invalid query format. Query must be a string."}), 400

    # Retrieve and process documents
    response = rag_chain.invoke({"question": query})
    print(response)

    response_answer = {"answer": response}
    return jsonify(response_answer)

 
# @app.route('/api', methods=['POST'])
# def retrieve():
#     print("post /ai called")
#     data = request.json
#     query = data.get("query")

#     print(f"query: {query}")
#     vector_store = MongoDBAtlasVectorSearch(
#     collection=MONGODB_COLLECTION,
#     embedding=embeddings,
#     index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
#     relevance_score_fn="cosine"
#     )

#     retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 6})


#         # RAG Chain setup
#     rag_chain = (
#         {"context": retriever | format_docs, "question": RunnablePassthrough()}
#         | prompt | llm | StrOutputParser()
#     )

#     # Within your retrieve function:
#     response = rag_chain.invoke({"question": query})

#     print(f"Query: {query}")
#     print(f"Formatted Docs: {format_docs(retriever.retrieve(query))}")


    
#     # # RAG Chain
#     # rag_chain = (
#     # {"context": retriever | format_docs, "question": RunnablePassthrough()}
#     # | prompt | llm | StrOutputParser()
#     # )

 
#     # response = rag_chain.invoke({ "question": query})
#     # response = llm.invoke(query)

#     print(response)

#     response_answer = {"answer": response}
#     return response_answer
#     # if not query:
#     #     return jsonify({"error": "Query is required"}), 400
 
    # # Use RAG chain to get response
    # response = rag_chain.invoke({"context": retriever.retrieve(query), "question": query})
 
    # return jsonify({"response": response})



# @app.route('/api/retrieve', methods=['POST'])
# def retrieve():
#     data = request.json
#     query = data.get("query")
#     if not query:
#         return jsonify({"error": "Query is required"}), 400
 
#     # Use RAG chain to get response
#     response = rag_chain.invoke({"context": retriever.retrieve(query), "question": query})
 
#     return jsonify({"response": response})
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)