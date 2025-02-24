from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import re
import logging

load_dotenv()


logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


db_uri = f"postgresql://postgres:{os.getenv('DB_PASSWORD')}@localhost:5432/postgres"
db = SQLDatabase.from_uri(db_uri)


llm = OllamaLLM(model="deepseek-r1:1.5b")
chain = create_sql_query_chain(llm, db)

def remove_code_fences(text: str) -> str:
    """
    Remove code fences (like ```sql ... ```) from the text.
    """

    match = re.search(r"```(?:sql)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    if text.startswith("```"):
        text = text.strip("`")
        parts = text.split("\n", 1)
        if len(parts) == 2 and parts[0].strip().lower() == "sql":
            text = parts[1]
    return text.strip()

def analyze_sql_error(error: str) -> str:
    """
    Analyze the SQL error message and return a hint message for correction.
    """
    hints = []
    lower_error = error.lower()
    if "syntax" in lower_error:
        hints.append("SQL syntax appears to be incorrect. Ensure correct quoting, parentheses, and overall structure as per PostgreSQL conventions.")
    if "does not exist" in lower_error:
        hints.append("A referenced table, column, or alias may not exist. Verify all names and their spelling.")
    if "operator" in lower_error or "type" in lower_error:
        hints.append("There might be an issue with operators or data type mismatches. Check that comparisons match the correct data types.")
    if "permission" in lower_error:
        hints.append("Insufficient permissions to execute the query. Ensure the database user has the required privileges.")
    if "timeout" in lower_error:
        hints.append("The query is taking too long to execute. Consider optimizing the query or checking database performance.")
    if not hints:
        hints.append("Review the error message carefully and adjust the query accordingly.")
    return " ".join(hints)

def correct_query(original_query: str, error: str, attempt: int, previous_errors: list) -> str:
    """
    Uses the language model to intelligently correct a SQL query based on the provided error message.
    The correction prompt emphasizes using accurate PostgreSQL syntax, and if multiple attempts have
    failed, it instructs the model to completely re-write the query from scratch.
    """

    extra_hint = ""
    if attempt > 1:
        extra_hint = (
            "Previous correction attempts have failed. Please analyze the error thoroughly and re-write "
            "the entire SQL query from scratch, ensuring that all issues are resolved."
        )

    detailed_hint = analyze_sql_error(error)
    
    history = ""
    if previous_errors:
        history = "Previous Errors and Corrections:\n"
        for idx, err in enumerate(previous_errors, 1):
            history += f"Attempt {idx}:\nError: {err['error']}\nCorrected Query: {err['query']}\n\n"

    combined_hint = " ".join(filter(None, [extra_hint, detailed_hint])).strip()
    if combined_hint:
        combined_hint += "\n\n"

    template_str = (
        "You are an advanced SQL assistant helping to correct PostgreSQL queries.\n\n"
        f"{history}"
        f"Attempt Number: {attempt}\n\n"
        "The following SQL query produced an error:\n\n"
        f"Error Message: {error}\n\n"
        "SQL Query:\n{query}\n\n"
    )
    template_str += combined_hint
    template_str += (
        "Please generate a corrected version of the SQL query that runs correctly on PostgreSQL. "
        "Output only the SQL query and nothing else—do not include any markdown formatting or extra commentary. "
        "Ensure strict adherence to PostgreSQL syntax and best practices."
    )

    prompt_template = ChatPromptTemplate.from_template(template_str)

    correction_chain = prompt_template | llm | StrOutputParser()
    logging.info(f"Sending correction prompt to LLM (Attempt {attempt}).")
    fixed = correction_chain.invoke({"error": error, "query": original_query, "attempt": attempt})
    corrected_query = remove_code_fences(fixed)
    logging.info("Received corrected query from LLM.")
    return corrected_query

def main():

    question = input("Masukkan pertanyaan: \n")
    logging.info("Generating initial SQL query based on user question.")
    query = chain.invoke({"question": question})
    query = remove_code_fences(query)
    print("SQL Query yang dihasilkan: ", query)

    max_attempts = 10
    attempt = 0
    result = None
    previous_errors = []

    while attempt < max_attempts:
        try:
            logging.info(f"Executing SQL query (Attempt {attempt + 1}).")
            result = db.run(query)
            logging.info("SQL query executed successfully.")
            break  # Exit the loop if the query executes successfully.
        except Exception as e:
            attempt += 1
            error_message = str(e)
            previous_errors.append({"error": error_message, "query": query})
            print(f"Error encountered during query execution (attempt {attempt}): {error_message}")
            logging.error(f"SQL execution error: {error_message}")
            
            # Provide more intelligent decision-making based on error types
            if "permission" in error_message.lower():
                print("It seems there are permission issues. Please check your database credentials and permissions.")
                logging.error("Permission issues detected. Aborting further attempts.")
                break
            elif "timeout" in error_message.lower():
                print("The query is taking too long to execute. Consider optimizing the query or checking database performance.")
                logging.warning("Query timeout detected. Suggesting optimization.")
            
            query = correct_query(query, error_message, attempt, previous_errors)
            print(f"SQL Query setelah perbaikan otomatis (attempt {attempt}): {query}")
    else:
        print("Max correction attempts reached. Query execution failed.")
        logging.error("Max correction attempts reached without successful execution.")
    
    if result is not None:
        print("Hasil Query: ", result)
    else:
        print("Tidak ada hasil yang dapat ditampilkan.")

if __name__ == "__main__":
    main()
