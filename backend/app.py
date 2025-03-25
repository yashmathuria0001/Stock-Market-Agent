import os
import yfinance as yf
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv
import json
import re
import requests
#  Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

#  Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

#  Initialize Gemini AI
llm = GoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GEMINI_API_KEY)

#  Stock Functions
def get_stock_price(ticker: str) -> dict:
    try:
        ticker = ticker.strip().upper()  # Clean input
        stock = yf.Ticker(ticker)
        history = stock.history(period="1d")

        if history.empty:
            return {"error": f"No stock price data available for {ticker}."}

        price = history["Close"].iloc[-1]

        return {
            "ticker": ticker,
            "latest_price": f"${price:.2f}",
            "recommendation": "INFO",
            "color": "BLUE",
            "reason": f"The latest stock price of {ticker} is ${price:.2f}.",
            "detailed_analysis": "No analysis available, this is just the latest price."
        }

    except IndexError:
        return {"error": f"Stock price data not available for {ticker}."}
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

        #AI-Powered Price Range Analysis
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

        # Fetch Financial Data
        earnings_growth = stock.info.get("earningsQuarterlyGrowth", None)
        debt_to_equity = stock.info.get("debtToEquity", None)
        pe_ratio = stock.info.get("trailingPE", None)

        # Placeholder for Market Trends & News (Replace with Real API Data)
        market_trends = "Stable market with moderate growth."
        news_summary = "No major negative news."
        company_financials = "Moderate earnings growth reported."

        # Recommendation Criteria
        recommendation = "HOLD"
        color = "YELLOW"

        if yearly_change > 20 and earnings_growth and earnings_growth > 0.1:
            recommendation, color = "BUY", "GREEN"
        elif yearly_change < -10 or (debt_to_equity and debt_to_equity > 200) or (earnings_growth and earnings_growth < -0.1):
            recommendation, color = "SELL", "RED"
        elif -10 <= yearly_change <= 20 and (earnings_growth is None or -0.1 <= earnings_growth <= 0.1):
            recommendation, color = "HOLD", "YELLOW"

        # AI-Powered Stock Analysis Prompt
        prompt = f"""
        You are a professional financial analyst providing stock investment recommendations.
        Analyze the stock {ticker} based on historical performance, financial indicators, market conditions, and news.

        ### Stock Data:
        - **Latest Price:** ${latest_price:.2f}
        - **1-Year Change:** {yearly_change:.2f}%
        - **Market Trends:** {market_trends}
        - **Recent News Impact:** {news_summary}
        - **Company Financials:** {company_financials}
        - **Debt-to-Equity Ratio:** {debt_to_equity}
        - **Earnings Growth:** {earnings_growth}
        - **P/E Ratio:** {pe_ratio}

        ### Decision Criteria:
        - **BUY (GREEN)** → If stock has strong momentum (>20% increase), positive earnings growth, or strong fundamentals.
        - **HOLD (YELLOW)** → If stock is stable (-10% to +20% change), with mixed trends and moderate future potential.
        - **SELL (RED)** → If stock has declined (>10%), high debt (>200%), negative earnings growth, or poor market conditions.

        ### Strict JSON Output:
        {{
          "ticker": "{ticker}",
          "latest_price": "${latest_price:.2f}",
          "yearly_change": "{yearly_change:.2f}%",
          "debt_to_equity": "{debt_to_equity}",
          "earnings_growth": "{earnings_growth}",
          "recommendation": "{recommendation}",
          "color": "{color}",
          "reason": "Summarize the investment decision in one sentence.",
          "detailed_analysis": "Explain the decision using stock performance, market trends, and financials."
        }}
        - **No Markdown, no extra text, only valid JSON.**
        """

        # AI Response
        ai_response = llm.invoke(prompt).strip()

        # Extract JSON Using Regex
        match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if match:
            response_dict = json.loads(match.group(0))
        else:
            response_dict = {"error": "AI response format is invalid."}

        return response_dict

    except Exception as e:
        return {"error": f"Error analyzing stock {ticker}: {str(e)}"}



def compare_stocks(ticker1: str, ticker2: str):
    """Compares two stocks based on their yearly performance."""
    try:
        stock1 = yf.Ticker(ticker1)
        stock2 = yf.Ticker(ticker2)

        history1 = stock1.history(period="1y")
        history2 = stock2.history(period="1y")

        if history1.empty or history2.empty:
            return {"error": f"Could not fetch data for {ticker1} or {ticker2}."}

        latest_price1 = history1["Close"].iloc[-1]
        latest_price2 = history2["Close"].iloc[-1]

        first_price1 = history1["Close"].iloc[0]
        first_price2 = history2["Close"].iloc[0]

        change1 = ((latest_price1 - first_price1) / first_price1) * 100
        change2 = ((latest_price2 - first_price2) / first_price2) * 100

        return {
            "comparison": {
                ticker1: {"price": f"${latest_price1:.2f}", "yearly_change": f"{change1:.2f}%"},
                ticker2: {"price": f"${latest_price2:.2f}", "yearly_change": f"{change2:.2f}%"}
            },
            "recommendation": "COMPARE",
            "color": "YELLOW",
            "reason": f"Comparison of {ticker1} and {ticker2} stock performance over the last year."
        }

    except Exception as e:
        return {"error": f"Error comparing {ticker1} and {ticker2}: {str(e)}"}


#  Unified API: Process Query and Return Formatted Response
@app.route("/ask_agent", methods=["POST"])
def ask_agent():
    data = request.json
    query = data.get("query", "").lower()

    if not query:
        return jsonify({"error": "Query is required"}), 400

    #  AI determines the best function to call
    decision_prompt = f"""
    You are a stock market assistant. The user asked: "{query}"

    Decide the best function to call:
    - If the user asks for **current price** → Return "CALL get_stock_price <TICKER>"
    - If the user asks for **stock analysis (buy/sell/hold)** → Return "CALL analyze_stock <TICKER>"
    - If the user asks for a **price range (support/resistance levels, entry/exit prices)** → Return "CALL get_stock_range <TICKER>"
    - If the user asks to **compare stocks** → Return "CALL compare_stocks <TICKER1> <TICKER2>"
    - If unclear, return: "UNKNOWN"
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
    elif "CALL compare_stocks" in decision:
        parts = decision.split()
        ticker1, ticker2 = parts[-2], parts[-1]
        response = compare_stocks(ticker1, ticker2)
    else:
        response = {"error": "I couldn't understand your request. Please try again."}

    return jsonify(response)




#  Run Flask App
if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))  # Get port from .env, default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)