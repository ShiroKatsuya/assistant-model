from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
import os
import re

load_dotenv()

# Membuat koneksi ke database
db_uri = f"postgresql://postgres:{os.getenv('DB_PASSWORD')}@localhost:5432/postgres"
db = SQLDatabase.from_uri(db_uri)
llm = OllamaLLM(model="llama2:7b")
chain = create_sql_query_chain(llm, db)

def format_sql_response(response: str) -> str:
    match = re.search(
        r'(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|WITH|VALUES)\b',
        response,
        re.IGNORECASE
    )
    if match:
        start = match.start()
        pre_sql = response[:start].strip()
        sql_part = response[start:].strip()
        commented_pre_sql = "\n".join("-- " + line for line in pre_sql.splitlines() if line.strip())
        
        if commented_pre_sql:
            formatted = commented_pre_sql + "\n" + sql_part
        else:
            formatted = sql_part
        return formatted
    else:
        return "\n".join("-- " + line for line in response.splitlines() if line.strip())

def remove_code_fences(text: str) -> str:
    match = re.search(r"```(?:sql)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    if text.startswith("```"):
        text = text.strip("`")
        parts = text.split("\n", 1)
        if len(parts) == 2 and parts[0].strip().lower() == "sql":
            text = parts[1]
    return text.strip()

question = input("Masukkan pertanyaan: \n")
query = chain.invoke({"question": question})
query = remove_code_fences(query)  # Remove any code fences from LLM output

generated_query = format_sql_response(query)
print("SQL Query yang dihasilkan: ", generated_query)

sql_match = re.search(
    r'(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|WITH|VALUES)\b.*',
    generated_query,
    re.IGNORECASE | re.DOTALL
)

if sql_match:
    sql_command = sql_match.group(0).strip()
    print("Extracted SQL command:\n", sql_command)

    try:
        result = db.run(sql_command)
        print("Query executed successfully.")
        print("Result: ", result)
    except Exception as e:
        print("Error executing SQL query:", e)
else:
    print("Error: Generated output does not contain a valid SQL query.")