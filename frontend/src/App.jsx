import { useState } from "react";
import axios from "axios";

function App() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAskAgent = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setResponse(null);

    try {
      const res = await axios.post("http://127.0.0.1:5000/ask_agent", { query });
      setResponse(res.data);
    } catch (error) {
      setResponse({ recommendation: "ERROR", reason: "Could not fetch data." });
    }
    setLoading(false);
  };

  const getBoxColor = () => {
    if (!response) return "bg-gray-300";
    if (response.recommendation === "ERROR") return "bg-red-500";
    if (response.recommendation === "RANGE") return "bg-blue-500";
    if (response.recommendation === "COMPARE") return "bg-yellow-500";
    if (response.color === "GREEN") return "bg-green-500";
    if (response.color === "YELLOW") return "bg-yellow-500";
    if (response.color === "RED") return "bg-red-500";
    return "bg-gray-300";
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-6">
      <h1 className="text-2xl font-bold mb-4">Stock Market AI Agent</h1>
      <input 
        type="text" 
        className="border p-2 rounded w-80" 
        placeholder="Ask about any stock, market trend, or sector..." 
        value={query} 
        onChange={(e) => setQuery(e.target.value)} 
      />
      <button 
        className="bg-blue-500 text-white px-4 py-2 mt-3 rounded" 
        onClick={handleAskAgent}
      >
        {loading ? "Processing..." : "Ask AI"}
      </button>

      {/* Display General Recommendation */}
      {response && response.recommendation !== "RANGE" && response.recommendation !== "COMPARE" && (
        <div className={`mt-4 p-3 text-white shadow rounded w-80 ${getBoxColor()}`}>
          <strong>Recommendation: {response.recommendation}</strong>
          <p>{response.reason}</p>
        </div>
      )}

      {/* Display Price Range Information */}
      {response && response.recommendation === "RANGE" && (
        <div className="mt-4 p-3 bg-blue-100 shadow rounded w-80 text-black">
          <strong>Price Range for {response.ticker}:</strong>
          <p><strong>High:</strong> {response.high_price}</p>
          <p><strong>Low:</strong> {response.low_price}</p>
          <p>{response.reason}</p>
        </div>
      )}

      {/* Display Stock Comparison */}
      {response && response.recommendation === "COMPARE" && (
        <div className="mt-4 p-3 bg-yellow-100 shadow rounded w-80 text-black">
          <strong>Stock Comparison:</strong>
          <p><strong>{Object.keys(response.comparison)[0]}</strong>: {response.comparison[Object.keys(response.comparison)[0]].price} ({response.comparison[Object.keys(response.comparison)[0]].yearly_change})</p>
          <p><strong>{Object.keys(response.comparison)[1]}</strong>: {response.comparison[Object.keys(response.comparison)[1]].price} ({response.comparison[Object.keys(response.comparison)[1]].yearly_change})</p>
          <p>{response.reason}</p>
        </div>
      )}

      {/* Display Market Trends */}
      {response && response.market_trend && (
        <div className="mt-4 p-3 bg-green-100 shadow rounded w-80 text-black">
          <strong>Market Trends:</strong>
          {Object.entries(response.market_trend).map(([index, value]) => (
            <p key={index}><strong>{index}:</strong> {value}</p>
          ))}
          <p>{response.reason}</p>
        </div>
      )}

      {/* Display Sector Performance */}
      {response && response.sector && (
        <div className="mt-4 p-3 bg-blue-100 shadow rounded w-80 text-black">
          <strong>Sector Performance: {response.sector}</strong>
          {Object.entries(response.stocks).map(([ticker, price]) => (
            <p key={ticker}><strong>{ticker}:</strong> {price}</p>
          ))}
          <p>{response.reason}</p>
        </div>
      )}

      {/* Display News */}
      {response && response.news_url && (
        <div className="mt-4 p-3 bg-white shadow rounded w-80 text-blue-600">
          <strong>Latest News for {response.ticker}:</strong>
          <a href={response.news_url} target="_blank" rel="noopener noreferrer" className="underline">Read More</a>
        </div>
      )}

      {/* Display Detailed Analysis */}
      {response && response.detailed_analysis && response.recommendation !== "RANGE" && (
        <div className="mt-4 p-3 bg-white shadow rounded w-80">
          <strong>Detailed Analysis:</strong>
          <p>{response.detailed_analysis}</p>
        </div>
      )}
    </div>
  );
}

export default App;
