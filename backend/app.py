import os
import yfinance as yf
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv
import json
import re
# ✅ Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ✅ Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# ✅ Initialize Gemini AI
llm = GoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GEMINI_API_KEY)

# ✅ Stock Functions
def get_stock_price(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")["Close"].iloc[-1]
        return {
            "ticker": ticker,
            "latest_price": f"${price:.2f}",
            "recommendation": "INFO",
            "color": "BLUE",
            "reason": f"The latest stock price of {ticker} is ${price:.2f}.",
            "detailed_analysis": "No analysis available, this is just the latest price."
        }
    except Exception as e:
        return {"error": f"Error fetching stock price for {ticker}: {str(e)}"}

def analyze_stock(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="1y")

        if history.empty:
            return {"error": f"Could not fetch data for {ticker}. Try again later."}

        latest_price = history["Close"].iloc[-1]
        last_year_price = history["Close"].iloc[0]
        yearly_change = ((latest_price - last_year_price) / last_year_price) * 100

        # 🔹 AI-Powered Stock Analysis Prompt
        prompt = f"""
        Analyze the stock {ticker} and provide a structured recommendation.

        Key Data:
        - Latest Price: ${latest_price:.2f}
        - Yearly Change: {yearly_change:.2f}%

        **Return ONLY a valid JSON object** in the following format:
        ```json
        {{
          "ticker": "{ticker}",
          "latest_price": "${latest_price:.2f}",
          "yearly_change": "{yearly_change:.2f}%",
          "recommendation": "BUY / HOLD / SELL",
          "color": "GREEN / YELLOW / RED",
          "reason": "Short summary of decision",
          "detailed_analysis": "Full explanation with market insights"
        }}
        ```
        - Do **not** include explanations before or after the JSON.
        - Do **not** use markdown formatting.
        - Ensure the output is **valid JSON** only.
        """

        ai_response = llm.invoke(prompt).strip()

        # ✅ Extract JSON using regex (removes extra text)
        match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if match:
            json_str = match.group(0)  # Extracts the valid JSON part
            response_dict = json.loads(json_str)  # Converts to Python dictionary
        else:
            response_dict = {"error": "AI response format is invalid."}

        return response_dict

    except Exception as e:
        return {"error": f"Error analyzing stock {ticker}: {str(e)}"}

# ✅ Unified API: Process Query and Return Formatted Response
@app.route("/ask_agent", methods=["POST"])
def ask_agent():
    data = request.json
    query = data.get("query", "")

    if not query:
        return jsonify({"error": "Query is required"}), 400

    # 🔍 AI determines the best function to call
    decision_prompt = f"""
    You are a stock market assistant. The user asked: "{query}"

    Decide the best function to call:
    - For stock price: "CALL get_stock_price <TICKER>"
    - For stock analysis: "CALL analyze_stock <TICKER>"
    - If unclear, return: "UNKNOWN"

    Example:
    - "Should I buy Microsoft?" -> "CALL analyze_stock MSFT"
    """

    decision = llm.invoke(decision_prompt).strip()

    if "CALL get_stock_price" in decision:
        ticker = decision.split()[-1]
        response = get_stock_price(ticker)
    elif "CALL analyze_stock" in decision:
        ticker = decision.split()[-1]
        response = analyze_stock(ticker)
    else:
        response = {"error": "I couldn't understand your request. Please try again."}

    # ✅ Ensure response is a dictionary
    if isinstance(response, str):  
        try:
            response = json.loads(response)  # Convert string to JSON
        except json.JSONDecodeError:
            response = {"error": "Invalid AI response format."}

    # ✅ Properly format AI response
    formatted_response = {
        "ticker": response.get("ticker", "Unknown"),
        "latest_price": response.get("latest_price", "N/A"),
        "yearly_change": response.get("yearly_change", "N/A"),
        "recommendation": response.get("recommendation", "Unknown"),
        "color": response.get("color", "GRAY"),
        "reason": response.get("reason", "No reason provided"),
        "detailed_analysis": response.get("detailed_analysis", "No detailed analysis available.")
    }

    return jsonify(formatted_response)



# ✅ Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
