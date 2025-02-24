from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
import os
import re  # import regex untuk mengekstrak perintah SQL

load_dotenv()

# Connect ke PostgreSQL database.
db_uri = f"postgresql://postgres:{os.getenv('DB_PASSWORD')}@localhost:5432/postgres"
db = SQLDatabase.from_uri(db_uri)

# Inisialisasi LLM (menggunakan model Llama2).
llm = OllamaLLM(model="llama2:7b")

# Buat chain yang menerjemahkan bahasa alami ke query SQL.
chain = create_sql_query_chain(llm, db)

def format_sql_response(response: str) -> str:
    """
    Mengubah keluaran menjadi format SQL dengan mengomentari bagian yang
    dianggap bukan SQL. Bagian sebelum (atau sesudah) perintah SQL utama akan
    ditambahkan komentar "--".
    
    Misal, jika response adalah:
      "Some commentary text.
       CREATE TABLE users (id INT, nama TEXT, email TEXT);
       Additional notes."
    
    Maka hasilnya adalah:
      "-- Some commentary text.
       CREATE TABLE users (id INT, nama TEXT, email TEXT);
       -- Additional notes."
    """
    # Cari awal perintah SQL (dengan kata kunci umum)
    match = re.search(
        r'(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|WITH|VALUES)\b',
        response,
        re.IGNORECASE
    )
    if match:
        start = match.start()
        # Bagian sebelum perintah SQL dianggap sebagai komentar
        pre_sql = response[:start].strip()
        # Bagian utama SQL (dianggap dari kata kunci pertama hingga akhir)
        sql_part = response[start:].strip()
        # Format setiap baris di pre_sql dengan prefix "-- "
        commented_pre_sql = "\n".join("-- " + line for line in pre_sql.splitlines() if line.strip())
        # Jika ada juga teks setelah SQL (misal komentar tambahan), 
        # kita dapat mencoba mencari tanda titik koma di akhir SQL dan memisahkan sisanya.
        # Untuk kesederhanaan, jika ada teks pasca SQL, kita komentari juga.
        # Cek apakah ada teks setelah SQL yang mungkin tidak valid.
        # Pada contoh regex sebelumnya, sql_part mengambil sampai akhir sehingga 
        # biasanya "post SQL" text tidak muncul.
        #
        # Gabungkan bagian yang telah dikomentari dan perintah SQL.
        if commented_pre_sql:
            formatted = commented_pre_sql + "\n" + sql_part
        else:
            formatted = sql_part
        return formatted
    else:
        # Jika tidak ada perintah SQL terdeteksi, komentari seluruh response.
        return "\n".join("-- " + line for line in response.splitlines() if line.strip())

# Terima masukan dari pengguna.
question = input("Masukkan pertanyaan (misal: 'Buat tabel users dengan kolom id, nama, dan email'): \n")

# Chain menghasilkan keluaran dari pertanyaan.
generated_query = chain.invoke({"question": question})
print("Generated query output:\n", generated_query)

# Tampilkan keluaran dengan format SQL: kalimat yang bukan SQL dikomentari.
formatted_query = format_sql_response(generated_query)
print("Formatted query with SQL comments:\n", formatted_query)

# Ekstrak perintah SQL menggunakan regex. Regex ini mencari kata kunci SQL umum.
sql_match = re.search(
    r'(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|WITH|VALUES)\b.*',
    generated_query,
    re.IGNORECASE | re.DOTALL
)

if sql_match:
    sql_command = sql_match.group(0).strip()
    print("Extracted SQL command:\n", sql_command)

    try:
        # Eksekusi hanya perintah SQL yang telah diekstrak.
        result = db.run(sql_command)
        print("Query executed successfully.")
        print("Result: ", result)
    except Exception as e:
        print("Error executing SQL query:", e)
else:
    print("Error: Generated output does not contain a valid SQL query.")
