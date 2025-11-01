from flask import Flask, request, jsonify
import pandas as pd
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# ---------------- CONFIG ----------------
CSV_PATH = "property_clean.csv"
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Get the API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

app = Flask(__name__)

# ---------------- LOAD CSV ----------------
df = pd.read_csv(CSV_PATH)

# Build embeddings using search_text column
embeddings = model.encode(df["search_text"].tolist())
dimension = embeddings.shape[1]
embeddings_func = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': "cpu"})


vector_store = FAISS.from_texts(df["search_text"].tolist(), embeddings_func)


# ------------ QUERY PARSER ---------------
def parse_user_query(q):
    q = q.lower()

    city_regex = r"(pune|mumbai|bangalore|bengaluru|hyderabad|delhi)"
    bhk_regex = r"(\d\s?bhk)"
    budget_regex = r"under\s?₹?([\d\.]+)\s?(cr|crore|lakh|lac|l)?"

    city = re.search(city_regex, q)
    bhk = re.search(bhk_regex, q)
    budget = re.search(budget_regex, q)

    parsed = {
        "city": city.group(1) if city else None,
        "bhk": bhk.group(1).upper().replace(" ", "") if bhk else None,
        "budget": None
    }

    if budget:
        val = float(budget.group(1))
        unit = budget.group(2)

        if unit in ["cr", "crore"]:
            parsed["budget"] = val * 10000000
        elif unit in ["lakh", "lac", "l"]:
            parsed["budget"] = val * 100000

    return parsed


# ----------- SEMANTIC SEARCH ----------
def semantic_search(query, k=10):
    context = vector_store.similarity_search(query, k=15)
    context_texts = [doc.page_content for doc in context]
    return df[df['search_text'].isin(context_texts)]

# -------------- FILTER RESULTS --------------
def apply_filters(df_results, parsed):
    filtered = df_results.copy()

    if parsed["city"]:
        filtered = filtered[filtered["city"].str.lower() == parsed["city"]]

    if parsed["bhk"]:
        filtered = filtered[filtered["type"].str.upper() == parsed["bhk"]]

    if parsed["budget"]:
        filtered = filtered[filtered["price"] <= parsed["budget"]]

    return filtered


# ------------- SUMMARY WITH GEMINI --------------
def generate_summary(df_results, user_query):
    text_block = "\n".join([
        f"{row.projectName}, {row.type}, located at {row.landmark} {row.city}, Price ₹{row.price}, Status {row.status}"
        for _, row in df_results.iterrows()
    ])

    prompt = f"""
User query:
{user_query}

Property Data:
{text_block}


"""

    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="""You are a real-estate assistant. Use ONLY the given CSV data.Write a factual 3-4 line summary. Do not hallucinate. give price in crore/lakh format.
            if no results found reply graciously for example "No ready 3BHK options found under ₹1.2 Cr in Baner. Expanding search to Wakad and Thergaon found 4 options." 
            MUST NOT used terms like "provided data" act as if you are assistant only."""),
        contents= prompt
    )

    return resp.text


# ----------- MAIN API ROUTE --------------
@app.route("/query", methods=["POST"])
def process_query():
    data = request.json
    user_query = data.get("query")

    parsed = parse_user_query(user_query)

    semantic = semantic_search(user_query)
    #print(semantic)

    filtered = apply_filters(semantic, parsed)

    final_results = filtered if len(filtered) else semantic

    summary = generate_summary(final_results, user_query)

    return jsonify({
        "summary": summary,
        "results": final_results.to_dict(orient="records")
    })


if __name__ == "__main__":
    app.run(debug=True)
