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

# Menginisialisasi LLM, misalnya menggunakan GPT dari OpenAI
llm = OllamaLLM(model="llama2:7b")
chain = create_sql_query_chain(llm, db)

def remove_code_fences(text: str) -> str:
    """
    Remove code fences (like ```sql ... ```) from the text and extract only the SQL query.
    """
    # Attempt to extract SQL within code fences
    match = re.search(r"```(?:sql)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # If no code fences, extract lines starting with SQL keywords
    lines = text.splitlines()
    sql_lines = []
    for line in lines:
        if re.match(r'^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\b', line, re.IGNORECASE):
            sql_lines.append(line)
    return '\n'.join(sql_lines).strip()

def is_valid_sql(query: str) -> bool:
    """
    Basic validation to check if the query starts with a valid SQL keyword.
    """
    return bool(re.match(r'^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\b', query, re.IGNORECASE))

def execute_query_with_autocorrect(sql_query: str, max_attempts: int = 3):
    """
    Attempts to execute the given SQL query. If an error occurs, it invokes the LLM to attempt
    to fix the error and generate a corrected query. It repeats this process for up to max_attempts.
    
    Returns a tuple (result, final_query) if successful.
    """
    current_query = sql_query.strip()
    for attempt in range(max_attempts):
        try:
            print(f"\nAttempt {attempt + 1}: Executing Query:\n{current_query}\n")
            result = db.run(current_query)
            return result, current_query  # Return both the result and the final query
        except Exception as e:
            error_msg = str(e)
            print(f"Attempt {attempt + 1} failed with error: {error_msg}")
            
            # Generate a prompt with both the error message and the failed query.
            correction_prompt = (
                f"The following SQL query:\n\n{current_query}\n\n"
                f"resulted in the error:\n\n{error_msg}\n\n"
                "Please provide a corrected version of the SQL query that can run successfully."
            )
            
            corrected_query = llm.invoke(correction_prompt)
            corrected_query = remove_code_fences(corrected_query)
            # Clean up any debug tags if present
            corrected_query = corrected_query.replace("<think>", "").replace("</think>", "").strip()
            
            if not is_valid_sql(corrected_query):
                print("The corrected query returned is not valid SQL. Aborting further attempts.")
                break
            
            # If the corrected query is the same as the one that failed, no further progress can be made.
            if corrected_query == current_query:
                print("The corrected query is the same as before. Aborting further attempts.")
                break
            
            print("Corrected SQL Query:")
            print(corrected_query)
            current_query = corrected_query

    raise Exception("Query failed to execute properly after multiple correction attempts.")

if __name__ == "__main__":
    question = input("Masukkan pertanyaan: \n")
    query = chain.invoke({"question": question})
    clean_query = remove_code_fences(query)
    # Remove any <think> tags that might appear in the query
    clean_query = clean_query.replace("<think>", "").replace("</think>", "").strip()

    if is_valid_sql(clean_query):
        print("SQL Query yang dihasilkan: ", clean_query)
        try:
            result, final_query = execute_query_with_autocorrect(clean_query, max_attempts=3)
            print("\nFinal SQL Query yang digunakan: ", final_query)
            print("Hasil Query: ", result)
            
            explanation_prompt = (
                f"Question: {question}\n"
                f"Query result: {result}\n"
                "Please explain this result in a clear and concise way."
            )
            explanation = llm.invoke(explanation_prompt)
            print("Explanation: ", explanation)
        except Exception as e:
            print("Terjadi kesalahan saat menjalankan query setelah beberapa upaya perbaikan: ", e)
    else:
        print("Query yang dihasilkan bukan SQL yang valid:")
        print(clean_query)
