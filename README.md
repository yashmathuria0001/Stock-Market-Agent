# Stock Market AI Agent

This project is a **Stock Market AI Agent** that provides stock price analysis, trading recommendations, and price range analysis using AI. The backend is built with **Flask** and **yFinance**, and the frontend is built using **Vite + React**.

## Features
- Get **real-time stock prices**
- Analyze stocks with **BUY/HOLD/SELL** recommendations
- Fetch **price ranges** for stocks (support/resistance levels)
- AI-powered financial insights
- **REST API** with Flask & **React frontend** for interaction

---

## Installation & Setup

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/your-repo.git
cd your-repo
```

### 2️⃣ Backend Setup (Flask API)
#### Navigate to the backend folder:
```sh
cd backend
```
#### Create a Virtual Environment (Optional but Recommended)
```sh
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
```
#### Install Dependencies:
```sh
pip install -r requirements.txt
```
#### Configure `.env` File
Create a `.env` file inside the `backend` folder and add:
```sh
GEMINI_API_KEY=your_api_key_here
FLASK_PORT=5000
```
#### Run the Flask Server:
```sh
python app.py
```
The backend will be running on: `http://127.0.0.1:5000`

---

### 3️⃣ Frontend Setup (React + Vite)
#### Navigate to the frontend folder:
```sh
cd frontend
```
#### Install Dependencies:
```sh
npm install
```
#### Start the Development Server:
```sh
npm run dev
```
The frontend will be running on: `http://localhost:5173`

---

## API Endpoints
### 1️⃣ Ask the AI Agent
- **Endpoint:** `POST /ask_agent`
- **Request Body:**
```json
{
  "query": "Should I buy Apple?"
}
```
- **Response (Example for Price Recommendation):**
```json
{
  "ticker": "AAPL",
  "latest_price": "$150.00",
  "recommendation": "BUY",
  "color": "GREEN",
  "reason": "Apple has shown strong growth with a 25% yearly increase.",
  "detailed_analysis": "The stock has strong momentum, making it a good buy."
}
```
- **Response (Example for Price Range):**
```json
{
  "ticker": "AAPL",
  "high_price": "$170.00",
  "low_price": "$140.00",
  "recommendation": "RANGE",
  "color": "BLUE",
  "reason": "Support and resistance levels for trading decisions.",
  "detailed_analysis": "Key technical levels indicate potential entry and exit points."
}
```
<img src="/readmephotos/Screenshot 2025-03-25 212331.png" alt="Stock Analysis" width="600">
<img src="/readmephotos/Screenshot 2025-03-25 212556.png" alt="Stock Analysis" width="600">
<img src="/readmephotos/Screenshot 2025-03-25 212612.png" alt="Stock Analysis" width="600">


---

## Folder Structure
```
📦 your-repo/
 ┣ 📂 backend/       # Flask backend
 ┃ ┣ 📜 app.py       # Flask API main file
 ┃ ┣ 📜 requirements.txt  # Backend dependencies
 ┃ ┣ 📜 .env         # API keys and configurations
 ┃ ┗ 📂 ...          # Other backend files
 ┣ 📂 frontend/      # React + Vite frontend
 ┃ ┣ 📜 App.jsx      # Main React App
 ┃ ┣ 📜 index.jsx    # React entry point
 ┃ ┣ 📜 package.json # Frontend dependencies
 ┃ ┗ 📂 ...          # Other frontend files
 ┗ 📜 README.md      # This file
```

---

## How It Works
1. User enters a stock-related query in the frontend.
2. The frontend sends the request to the Flask API (`/ask_agent`).
3. The backend determines which function to call:
   - **get_stock_price** → Fetch latest stock price.
   - **analyze_stock** → Analyze whether to buy/hold/sell.
   - **get_stock_range** → Fetch support & resistance levels.
4. AI processes the request and returns JSON response.
5. The frontend displays the response with color-coded insights.

---

## Contributing
Feel free to fork and contribute to the project! 

