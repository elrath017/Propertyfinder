# 🏡 Property Finder - Real Estate AI Assistant

An intelligent real estate search application that combines semantic search with natural language processing to help users find properties matching their requirements. The system uses embeddings for semantic matching and Gemini AI for natural language summaries.

## 🌟 Features

- Natural language property search (e.g., "3BHK in Pune under 1 Cr")
# 🏡 Property Finder

Light-weight real-estate assistant that combines semantic search (Sentence Transformers + FAISS) with an AI summarizer (Google Gemini) to help find properties by natural-language queries.

This repository contains a Streamlit frontend (`app.py`) and a Flask backend (`backend.py`) that load a cleaned property dataset (`property_clean.csv`) and expose a `/query` endpoint for semantic property search.
## Setup guide

1. Create/activate a Python environment (PowerShell):

```powershell
# create 
python -m venv myenv

# activate 
.\myenv\Scripts\Activate.ps1 #write your environment name in place of myenv
```

2. Install dependencies:

```powershell
pip install -r "c:\Users\rahul\Desktop\NoBrokerage\Property Finder\requirements.txt"
```

3. Add your Gemini API key in a `.env` file at the project root:

```text
GEMINI_API_KEY=your_gemini_api_key_here
```

4. Start the backend (Flask):

```powershell
# from project root
python backend.py
```

5. Start the frontend (Streamlit) in a separate terminal:

```powershell
streamlit run app.py
```

6. Open the Streamlit UI in your browser (it will POST queries to the backend at `http://127.0.0.1:5000/query`).

## Examples

Example user queries and expected behavior:

- "3BHK in Pune under 1 Cr"
    - Backend: parse city `pune`, bhk `3BHK`, budget `10000000`; perform semantic search and apply filters.
    - Frontend: displays a 3–4 line factual summary and a list of matched properties.

- "2 BHK Mumbai under ₹80 lakh"
    - Backend: parse city `mumbai`, bhk `2BHK`, budget `8000000`; returns matching rows and summary.

- "Show ready to move 1BHK in Bangalore"
    - Backend: semantic search + filter by `city=bengaluru` (or bangalore) and `type=1BHK`.

Sample JSON response shape from the backend (`/query`):

```json
{
    "summary": "<3-4 line factual summary>",
    "results": [
        {
            "projectName": "Example Project",
            "type": "3BHK",
            "price": 9500000,
            "status": "READY_TO_MOVE",
            "landmark": "Baner",
            "city": "Pune",
            "fullAddress": "..."
        }
    ]
}
```



