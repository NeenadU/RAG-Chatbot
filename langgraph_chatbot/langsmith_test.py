from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
import time

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

response = llm.invoke("Hello")

print(response.content)

time.sleep(10)