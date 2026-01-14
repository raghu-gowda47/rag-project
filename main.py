import os
from src.data_loader import load_pdf
from src.text_splitter import split_documents
from src.vectorstore import create_vectorstore
from src.rag_chain import build_rag_chain

def main():
    pdf_path = os.path.join(os.path.dirname(__file__), "Ramayana.pdf")
    persist_directory = os.path.join(os.path.dirname(__file__), "chroma_db_bpe")
    docs = load_pdf(pdf_path)
    splits = split_documents(docs)
    vectorstore = create_vectorstore(splits, persist_directory)
    rag_chain = build_rag_chain(vectorstore)

    print("\n--- RAG Chatbot Ready ---")
    print("Type your questions about the PDF. Type 'exit' to quit.")
    while True:
        user_question = input("\nYour Question: ")
        if user_question.lower() == 'exit':
            print("Exiting chatbot.")
            break
        print("Searching and generating response...")
        response = rag_chain.invoke(user_question)
        print("\nAnswer:", response)

if __name__ == "__main__":
    main()