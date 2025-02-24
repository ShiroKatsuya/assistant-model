from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import re

load_dotenv()

# Create the database connection.
db_uri = f"postgresql://postgres:{os.getenv('DB_PASSWORD')}@localhost:5432/postgres"
db = SQLDatabase.from_uri(db_uri)

# Initialize the language model.
llm = OllamaLLM(model="llama3.2:1b")
chain = create_sql_query_chain(llm, db)

def remove_code_fences(text: str) -> str:
    # Try to extract text within a SQL code block (```sql ... ```)
    match = re.search(r"```(?:sql)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Fallback: if the text starts and ends with code fences, remove them.
    if text.startswith("```"):
        text = text.strip("`")
        parts = text.split("\n", 1)
        if len(parts) == 2 and parts[0].strip().lower() == "sql":
            text = parts[1]
    return text.strip()

def correct_query(original_query: str, error: str) -> str:
    # Construct a prompt that explains the error and asks the model to fix the query.
    prompt_template = ChatPromptTemplate.from_template(
        "The following SQL query produced an error:\n\nError: {error}\n\nSQL Query:\n{query}\n\nPlease fix the SQL query so that it runs correctly. Output only the corrected SQL query."
        "Just Focus on the SQL Query, don't include any other text."
        "Output only the corrected SQL query."
        "Using PostgreSQL syntax."
        
    )
    correction_chain = prompt_template | llm | StrOutputParser()
    fixed = correction_chain.invoke({"error": error, "query": original_query})
    return remove_code_fences(fixed)

# Get the user's question and generate an SQL query.
question = input("Masukkan pertanyaan: \n")
query = chain.invoke({"question": question})
query = remove_code_fences(query)
print("SQL Query yang dihasilkan: ", query)

# After the query is generated, check if it is meant for listing databases.
if "list databases" in question.lower() or "check all" in question.lower():
    # Override with the correct query to list databases
    query = "SELECT datname FROM pg_database WHERE datistemplate = false;"
    print("Mengganti query dengan query yang diperbaiki untuk mendapatkan daftar database.")

# Try to run the query with multiple correction attempts if needed.
max_attempts = 10
attempt = 0
while attempt < max_attempts:
    try:
        result = db.run(query)
        break
    except Exception as e:
        attempt += 1
        print(f"Error encountered during query execution (attempt {attempt}): {e}")
        query = correct_query(query, str(e))
        print(f"SQL Query setelah perbaikan otomatis (attempt {attempt}): {query}")
else:
    print("Max correction attempts reached. Query execution failed.")
    result = None

print("Hasil Query: ", result)
