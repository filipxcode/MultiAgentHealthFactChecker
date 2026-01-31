from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def chunk_text(data: list[Document], chunk_size: int, chunk_overlap: int) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
    separators=[
        "\n\n",
        "\n",  
        ".",   
        " ",   
        ""     
        ]
        )
    return text_splitter.split_documents(data)