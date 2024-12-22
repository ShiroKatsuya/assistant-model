import re

response = "**Ini adalah teks dengan tanda tebal**"
cleaned_response = re.sub(r"\*\*(.*?)\*\*", r"\1", response)
print(cleaned_response)  # Output: Ini adalah teks dengan tanda tebal
