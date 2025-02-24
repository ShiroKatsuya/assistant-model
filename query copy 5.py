from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to your PostgreSQL database.
# For operations like creating a database, you may need to connect to a maintenance database (e.g., "postgres")
db_uri = f"postgresql://postgres:{os.getenv('DB_PASSWORD')}@localhost:5432/postgres"
db = SQLDatabase.from_uri(db_uri)

# Initialize your LLM (here using a Llama2 model).
llm = OllamaLLM(model="llama2:7b")

# Create a SQL query chain that translates natural language into SQL.
chain = create_sql_query_chain(llm, db)

# Get a natural language instruction from the user.
question = input("Masukkan pertanyaan : \n")
# The chain generates a SQL query based on the provided question.
generated_query = chain.invoke({"question": question})
print("Generated SQL Query:\n", generated_query)

# Execute the generated SQL query.
try:
    # db.run() can execute any valid SQL statement including DDL and DML.
    result = db.run(generated_query)
    print("Query executed successfully.")
    print("Result: ", result)
except Exception as e:
    print("Error executing query:", e)
