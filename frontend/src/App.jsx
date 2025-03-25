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
    if (response.color === "GREEN") return "bg-green-500";
    if (response.color === "YELLOW") return "bg-yellow-500";
    if (response.color === "RED") return "bg-red-500";
    return "bg-gray-300";
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-6">
      <h1 className="text-2xl font-bold mb-4">Stock Market AI Agent</h1>
      <input type="text" className="border p-2 rounded w-80" placeholder="Ask about any stock..." value={query} onChange={(e) => setQuery(e.target.value)} />
      <button className="bg-blue-500 text-white px-4 py-2 mt-3 rounded" onClick={handleAskAgent}>{loading ? "Processing..." : "Ask AI"}</button>
      {response && <div className={`mt-4 p-3 text-white shadow rounded w-80 ${getBoxColor()}`}><strong>Recommendation: {response.recommendation}</strong><p>{response.reason}</p></div>}
      {response && response.detailed_analysis && <div className="mt-4 p-3 bg-white shadow rounded w-80"><strong>Detailed Analysis:</strong><p>{response.detailed_analysis}</p></div>}
    </div>
  );
}

export default App;
