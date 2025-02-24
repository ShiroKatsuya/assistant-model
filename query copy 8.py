import os
import re
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv

load_dotenv()

# Membuat koneksi ke database
db_uri = f"postgresql://postgres:{os.getenv('DB_PASSWORD')}@localhost:5432/postgres"
db = SQLDatabase.from_uri(db_uri)
llm = OllamaLLM(model="deepseek-r1:1.5b")
chain = create_sql_query_chain(llm, db)

question = input("Masukkan pertanyaan:\n")
response = chain.invoke({"question": question})
print("SQL Query yang dihasilkan: ", response)

# Define all regex patterns with the capturing group you want to extract.
# Pattern 1: Extracts SQL from a Markdown code block.
# Pattern 2: Looks for a SELECT ... FROM pattern, ending with ; or . or end-of-string.
# Pattern 3: A general pattern capturing various SQL commands.
patterns = [
    {"pattern": r"```sql\n(.*?)\n```", "group": 1},
    {"pattern": r"(?is)\bSELECT\b\s+.*?\s+\bFROM\b\s+.*?(?:;|\.|$)", "group": 0},
    {"pattern": r"(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|WITH|VALUES)\b.*", "group": 0},
]

# Try each pattern until a match is found.
sql_command = None
for pat in patterns:
    match = re.search(pat["pattern"], response, re.IGNORECASE | re.DOTALL)
    if match:
        sql_command = match.group(pat["group"]).strip()
        print("\nExtracted SQL Command using pattern:")
        print(f"{pat['pattern']}")
        print("Data:", sql_command)
        break

if not sql_command:
    print("\nNo valid SQL command found.")






