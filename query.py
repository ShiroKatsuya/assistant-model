from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
import os

load_dotenv()

# Membuat koneksi ke database
db_uri = f"postgresql://postgres:{os.getenv('DB_PASSWORD')}@localhost:5432/postgres"
db = SQLDatabase.from_uri(db_uri)
llm = OllamaLLM(model="deepseek-r1:1.5b")
chain = create_sql_query_chain(llm, db)
question = input("Masukkan pertanyaan: \n")
query = chain.invoke({"question": question})
print("SQL Query yang dihasilkan: ", query)





