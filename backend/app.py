import os
import yfinance as yf
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv

# ✅ Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ✅ Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# ✅ Initialize Gemini AI in LangChain
llm = GoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GEMINI_API_KEY)

# ✅ Stock Functions
def get_stock_price(ticker: str) -> str:
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")["Close"].iloc[-1]
        return f"The latest stock price of {ticker} is ${price:.2f}"
    except Exception as e:
        return f"Error fetching stock price for {ticker}: {str(e)}"

def get_finance_report(ticker: str) -> str:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        financials = stock.financials
        report = f"Company: {info.get('longName', ticker)}\n"
        report += f"Sector: {info.get('sector', 'N/A')}\n"
        report += "Recent Financials:\n"
        report += str(financials.head())
        return report
    except Exception as e:
        return f"Error fetching finance report for {ticker}: {str(e)}"

def analyze_stock(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period="1y")

        if history.empty:
            return {"error": f"Could not fetch data for {ticker}. Try again later."}

        latest_price = history["Close"].iloc[-1]
        last_year_price = history["Close"].iloc[0]
        yearly_change = ((latest_price - last_year_price) / last_year_price) * 100

        prompt = f"""
        Analyze the stock {ticker} and provide a structured recommendation.
        
        Key Data:
        - Latest Price: ${latest_price:.2f}
        - Yearly Change: {yearly_change:.2f}%
        
        Decide whether the stock is a **BUY, HOLD, or SELL** based on:
        - Market trends, industry performance, and financial health.
        - Revenue growth, profit margins, and valuation ratios.
        - Future outlook, potential risks, and opportunities.

        **Final Output Format (JSON):**
        ```json
        {{
          "ticker": "{ticker}",
          "latest_price": "{latest_price}",
          "yearly_change": "{yearly_change:.2f}%",
          "recommendation": "BUY / HOLD / SELL",
          "color": "GREEN / YELLOW / RED",
          "reason": "Brief summary",
          "detailed_analysis": "Full explanation of the recommendation."
        }}
        ```
        """

        response = llm.invoke(prompt)
        return response  # This will return the structured JSON
    except Exception as e:
        return {"error": f"Error analyzing stock {ticker}: {str(e)}"}


# ✅ Agent Route: Handle Free-Text Query
@app.route("/ask_agent", methods=["POST"])
def ask_agent():
    data = request.json
    query = data.get("query", "")

    if not query:
        return jsonify({"error": "Query is required"}), 400

    # 🔍 LLM decides which function to call
    decision_prompt = f"""
    You are a stock market assistant. The user asked: "{query}"

    Decide the best function to call:
    - For stock price: "CALL get_stock_price <TICKER>"
    - For stock analysis: "CALL analyze_stock <TICKER>"
    - For finance report: "CALL get_finance_report <TICKER>"
    - If unclear, return: "UNKNOWN"
    
    Examples:
    - "Tell me Apple's stock price" -> "CALL get_stock_price AAPL"
    - "Should I invest in Tesla?" -> "CALL analyze_stock TSLA"
    - "What is Amazon's latest rate?" -> "CALL get_stock_price AMZN"
    """

    decision = llm.invoke(decision_prompt).strip()

    if "CALL get_stock_price" in decision:
        ticker = decision.split()[-1]
        response = get_stock_price(ticker)
    elif "CALL analyze_stock" in decision:
        ticker = decision.split()[-1]
        response = analyze_stock(ticker)
    elif "CALL get_finance_report" in decision:
        ticker = decision.split()[-1]
        response = get_finance_report(ticker)
    else:
        response = "I couldn't understand your request. Please try again."

    return jsonify({"response": response})

# ✅ Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
