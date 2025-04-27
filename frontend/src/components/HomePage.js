import React, { useState, useEffect } from 'react';
import axios from 'axios';

const HomePage = () => {
  const [news, setNews] = useState([]);
  const [performanceData, setPerformanceData] = useState({
    stocks: [],
    mutualFunds: [],
    etfs: []
  });
  const [currentView, setCurrentView] = useState('stocks');
  const [timeLeft, setTimeLeft] = useState(20);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Mock data for mutual funds and ETFs
  const mockMutualFunds = [
    { symbol: "VFIAX", name: "Vanguard 500 Index", price: "432.18", change: "+1.25%" },
    { symbol: "FXAIX", name: "Fidelity 500 Index", price: "178.45", change: "+1.18%" },
    { symbol: "SWPPX", name: "Schwab S&P 500 Index", price: "68.92", change: "+1.22%" },
    { symbol: "VTSAX", name: "Vanguard Total Stock", price: "118.75", change: "+0.95%" },
    { symbol: "VBTLX", name: "Vanguard Total Bond", price: "10.25", change: "-0.15%" },
    { symbol: "PRMTX", name: "T. Rowe Price Growth", price: "142.65", change: "+1.75%" },
    { symbol: "AGTHX", name: "American Growth Fund", price: "65.87", change: "+0.92%" },
    { symbol: "FCNTX", name: "Fidelity Contrafund", price: "17.53", change: "+1.45%" },
    { symbol: "VWELX", name: "Vanguard Wellington", price: "45.76", change: "+0.35%" },
    { symbol: "VDIGX", name: "Vanguard Dividend Growth", price: "35.42", change: "+0.65%" }
  ];
  
  const mockETFs = [
    { symbol: "SPY", name: "SPDR S&P 500 ETF", price: "478.35", change: "+1.32%" },
    { symbol: "QQQ", name: "Invesco QQQ Trust", price: "425.67", change: "+1.85%" },
    { symbol: "VTI", name: "Vanguard Total Stock ETF", price: "252.18", change: "+1.05%" },
    { symbol: "VOO", name: "Vanguard S&P 500 ETF", price: "438.92", change: "+1.28%" },
    { symbol: "ARKK", name: "ARK Innovation ETF", price: "45.23", change: "-2.15%" },
    { symbol: "IVV", name: "iShares Core S&P 500", price: "475.12", change: "+1.30%" },
    { symbol: "VEA", name: "Vanguard FTSE Developed", price: "48.75", change: "+0.45%" },
    { symbol: "IEFA", name: "iShares Core MSCI EAFE", price: "72.38", change: "+0.55%" },
    { symbol: "AGG", name: "iShares Core US Aggregate", price: "108.25", change: "-0.25%" },
    { symbol: "BND", name: "Vanguard Total Bond ETF", price: "72.15", change: "-0.18%" }
  ];

  // Function to fetch data
  const fetchData = async () => {
    try {
      // Fetch business news from NewsAPI
      const newsResponse = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/newsapi/top-headlines?category=business&country=us`);
      const formattedNews = newsResponse.data.articles.map((item, index) => ({
        id: index,
        headline: item.title,
        summary: item.description || "No description available",
        datetime: new Date(item.publishedAt).toISOString(),
        source: item.source.name
      }));

      // Fetch stock data (using mock data from our backend)
      const stockSymbols = [
        "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", 
        "META", "NVDA", "JPM", "V", "JNJ"
      ];
      const stocksData = await Promise.all(
        stockSymbols.map(async (symbol) => {
          const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/stock/${symbol}`);
          return {
            symbol,
            name: response.data.name || getStockName(symbol),
            price: response.data.price.toFixed(2),
            change: `${response.data.change > 0 ? '+' : ''}${response.data.change.toFixed(2)}%`
          };
        })
      );

      setNews(formattedNews);
      setPerformanceData({
        stocks: stocksData,
        mutualFunds: mockMutualFunds,
        etfs: mockETFs
      });
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch data');
      setLoading(false);
    }
  };

  // Helper function to get stock names
  const getStockName = (symbol) => {
    const stockNames = {
      "AAPL": "Apple Inc.",
      "GOOGL": "Alphabet Inc.",
      "MSFT": "Microsoft Corp.",
      "AMZN": "Amazon.com Inc.",
      "TSLA": "Tesla Inc.",
      "META": "Meta Platforms Inc.",
      "NVDA": "NVIDIA Corp.",
      "JPM": "JPMorgan Chase & Co.",
      "V": "Visa Inc.",
      "JNJ": "Johnson & Johnson"
    };
    return stockNames[symbol] || symbol;
  };

  // Initial data fetch
  useEffect(() => {
    fetchData();
  }, []);

  // Rotate view every 20 seconds and update countdown timer
  useEffect(() => {
    const viewInterval = setInterval(() => {
      setCurrentView(current => {
        if (current === 'stocks') return 'mutualFunds';
        if (current === 'mutualFunds') return 'etfs';
        return 'stocks';
      });
      setTimeLeft(20);
    }, 20000);
    
    const timerInterval = setInterval(() => {
      setTimeLeft(prev => (prev > 0 ? prev - 1 : prev));
    }, 1000);
    
    return () => {
      clearInterval(viewInterval);
      clearInterval(timerInterval);
    };
  }, []);

  // Refresh data every 60 seconds
  useEffect(() => {
    const dataInterval = setInterval(() => {
      fetchData();
    }, 60000);
    
    return () => clearInterval(dataInterval);
  }, []);

  if (loading) return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>
  );

  if (error) return (
    <div className="bg-gray-900 min-h-screen flex items-center justify-center">
      <div className="text-red-500 text-center p-4">
        {error}
      </div>
    </div>
  );

  // Get current performance data based on view
  const getCurrentPerformanceData = () => {
    if (currentView === 'stocks') return performanceData.stocks;
    if (currentView === 'mutualFunds') return performanceData.mutualFunds;
    return performanceData.etfs;
  };

  // Get title for current view
  const getViewTitle = () => {
    if (currentView === 'stocks') return "Stock Performance";
    if (currentView === 'mutualFunds') return "Mutual Fund Performance";
    return "ETF Performance";
  };

  return (
    <div className="flex min-h-screen bg-gray-900">
      {/* Sidebar - Performance Data */}
      <div className="w-64 bg-gray-800 shadow-lg p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-white">{getViewTitle()}</h2>
          <div className="text-sm text-gray-400">{timeLeft}s</div>
        </div>
        
        {/* View selector */}
        <div className="flex justify-between mb-4 bg-gray-700 rounded-lg p-1">
          <button 
            className={`px-2 py-1 text-xs rounded ${currentView === 'stocks' ? 'bg-blue-600 text-white' : 'text-gray-300'}`}
            onClick={() => { setCurrentView('stocks'); setTimeLeft(20); }}
          >
            Stocks
          </button>
          <button 
            className={`px-2 py-1 text-xs rounded ${currentView === 'mutualFunds' ? 'bg-blue-600 text-white' : 'text-gray-300'}`}
            onClick={() => { setCurrentView('mutualFunds'); setTimeLeft(20); }}
          >
            Mutual Funds
          </button>
          <button 
            className={`px-2 py-1 text-xs rounded ${currentView === 'etfs' ? 'bg-blue-600 text-white' : 'text-gray-300'}`}
            onClick={() => { setCurrentView('etfs'); setTimeLeft(20); }}
          >
            ETFs
          </button>
        </div>
        <div className="space-y-4">
          {getCurrentPerformanceData().map((item) => (
            <div key={item.symbol} className="p-3 border border-gray-700 rounded-lg bg-gray-800">
              <div className="font-bold text-white">{item.symbol}</div>
              <div className="text-sm text-gray-400 mb-1">{item.name}</div>
              <div className="text-lg text-white">${item.price}</div>
              <div className={`text-sm ${item.change.startsWith('+') ? 'text-green-500' : 'text-red-500'}`}>
                {item.change}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content - News Cards */}
      <div className="flex-1 p-8 bg-gray-900">
        <h1 className="text-3xl font-bold mb-6 text-white">Stock Market News</h1>
        <div className="space-y-4">
          {news.map((item) => (
            <div key={item.id} className="bg-gray-800 rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-2 text-white">{item.headline}</h2>
              <p className="text-gray-300 mb-4">{item.summary}</p>
              <div className="flex justify-between text-sm text-gray-400">
                <span>{new Date(item.datetime).toLocaleDateString()}</span>
                <span>{item.source}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HomePage;
