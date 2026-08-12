from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
import google.generativeai as genai


gemini_router = APIRouter()

genai.configure(api_key="AIzaSyClsKVDfbcEBVN17ZBaCgEVkOZ19hAvAAE")


class Chatrequest(BaseModel):
    query:str


@gemini_router.post("/chat")
def getmini_chat(data:Chatrequest):
    query = data.query
    best_content = """
Hello Gemini, You are my travel adviser. I will provide you some information like Name, Gender, Country, 
Number of Days, Budget Type, Maximum Amount, Number of Travelers, Hotel Preferences, Food Options, 
Travel Mood/Place. 

Your task is to create a **Day-by-Day travel itinerary** for the given number of days. For each day, provide:

1. **Day X:** (e.g., Day 1)
2. **Morning:** Places to visit + suggested activities
3. **Afternoon:** Places to visit + lunch options
4. **Evening:** Places to visit + dinner options + any events
5. **Estimated Expenses:** Approximate cost for the day

**Rules:**
- Do NOT mention that you are AI or Gemini.
- Be concise and clear.
- If the question is not travel-related, reply: "Sorry we can't help you in this query, please ask me travel related questions."
- Avoid extra text; focus only on the itinerary and expenses.
"""
    
    prompt = f"Using the following content from{best_content}\n\nAnswer the question: {query} give me answer in short information"
    try:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        answer = response.text
    except Exception as e:
        answer = f"Gemini API error: {e}"

    return {
        "answer":answer
    }