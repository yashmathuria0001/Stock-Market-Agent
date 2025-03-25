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
    
def get_stock_range(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="6mo")

        if history.empty:
            return {"error": f"Could not fetch data for {ticker}."}

        # Compute price range using high/low values
        high_price = history["High"].max()
        low_price = history["Low"].min()

        # 🔹 AI-Powered Price Range Analysis
        prompt = f"""
        Determine the support and resistance levels for {ticker}.

        **Stock Data (Last 6 Months):**
        - **Highest Price:** ${high_price:.2f}
        - **Lowest Price:** ${low_price:.2f}

        Provide a JSON response in the following format:
        ```json
        {{
          "ticker": "{ticker}",
          "high_price": "${high_price:.2f}",
          "low_price": "${low_price:.2f}",
          "recommendation": "RANGE",
          "color": "BLUE",
          "reason": "Support and resistance levels for trading decisions.",
          "detailed_analysis": "Provide an explanation of key technical levels."
        }}
        ```
        - Do **not** include markdown.
        - Ensure **valid JSON output** only.
        """

        ai_response = llm.invoke(prompt).strip()

        match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if match:
            json_str = match.group(0)
            response_dict = json.loads(json_str)
        else:
            response_dict = {"error": "AI response format is invalid."}

        return response_dict

    except Exception as e:
        return {"error": f"Error fetching stock range for {ticker}: {str(e)}"}


def analyze_stock(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="1y")

        if history.empty:
            return {"error": f"Could not fetch data for {ticker}. Try again later."}

        latest_price = history["Close"].iloc[-1]
        last_year_price = history["Close"].iloc[0]
        yearly_change = ((latest_price - last_year_price) / last_year_price) * 100

        # 🔹 Define Recommendation Criteria
        recommendation = "HOLD"
        color = "YELLOW"
        if yearly_change > 20:
            recommendation, color = "BUY", "GREEN"
        elif yearly_change < -10:
            recommendation, color = "SELL", "RED"

        # 🔹 AI-Powered Stock Analysis Prompt
        prompt = f"""
        You are a financial analyst providing stock investment recommendations.
        Analyze the stock {ticker} using the following data and determine whether to BUY, HOLD, or SELL.

        **Stock Data:**
        - **Latest Price:** ${latest_price:.2f}
        - **1-Year Change:** {yearly_change:.2f}%
        - **Market Trends:** Consider the broader market and sector performance.

        **Decision Guidelines:**
        - **BUY** (GREEN) → If the stock has strong growth momentum (>20% yearly increase), positive news, or strong fundamentals.
        - **HOLD** (YELLOW) → If the stock is stable, with mixed trends and moderate future potential.
        - **SELL** (RED) → If the stock has dropped significantly (>10% decline) or faces financial risks.

        **Output Strict JSON Format:**
        ```json
        {{
          "ticker": "{ticker}",
          "latest_price": "${latest_price:.2f}",
          "yearly_change": "{yearly_change:.2f}%",
          "recommendation": "BUY / HOLD / SELL",
          "color": "GREEN / YELLOW / RED",
          "reason": "Provide a short summary of the decision.",
          "detailed_analysis": "Explain the decision using stock performance, market trends, and sector analysis."
        }}
        ```
        - Do **not** include markdown.
        - Do **not** add extra text before or after the JSON.
        - Ensure the output is **valid JSON** only.
        """

        ai_response = llm.invoke(prompt).strip()

        # ✅ Extract JSON using regex
        match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if match:
            json_str = match.group(0)
            response_dict = json.loads(json_str)
        else:
            response_dict = {"error": "AI response format is invalid."}

        return response_dict

    except Exception as e:
        return {"error": f"Error analyzing stock {ticker}: {str(e)}"}


# ✅ Unified API: Process Query and Return Formatted Response
@app.route("/ask_agent", methods=["POST"])
def ask_agent():
    data = request.json
    query = data.get("query", "").lower()

    if not query:
        return jsonify({"error": "Query is required"}), 400

    # 🔍 AI determines the best function to call
    decision_prompt = f"""
    You are a stock market assistant. The user asked: "{query}"

    Decide the best function to call:
    - If the user asks for **current price** → Return "CALL get_stock_price <TICKER>"
    - If the user asks for **stock analysis (buy/sell/hold)** → Return "CALL analyze_stock <TICKER>"
    - If the user asks for a **price range (support/resistance levels, entry/exit prices)** → Return "CALL get_stock_range <TICKER>"
    - If unclear, return: "UNKNOWN"

    Example:
    - "Should I buy Microsoft?" → "CALL analyze_stock MSFT"
    - "What is the range of buying NVIDIA?" → "CALL get_stock_range NVDA"
    - "What is Apple's current price?" → "CALL get_stock_price AAPL"
    """

    decision = llm.invoke(decision_prompt).strip()

    if "CALL get_stock_price" in decision:
        ticker = decision.split()[-1]
        response = get_stock_price(ticker)
    elif "CALL analyze_stock" in decision:
        ticker = decision.split()[-1]
        response = analyze_stock(ticker)
    elif "CALL get_stock_range" in decision:
        ticker = decision.split()[-1]
        response = get_stock_range(ticker)
    else:
        response = {"error": "I couldn't understand your request. Please try again."}

    return jsonify(response)




# ✅ Run Flask App
if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))  # Get port from .env, default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)