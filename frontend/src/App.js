import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import './App.css';
import HomePage from './components/HomePage';

// Configuration
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Helper function to format dates
const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return new Date(dateString).toLocaleDateString(undefined, options);
};

// Authentication context
import { createContext, useContext } from 'react';

const AuthContext = createContext(null);

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserProfile(token);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserProfile = async (token) => {
    try {
      const response = await axios.get(`${API}/users/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (error) {
      console.error("Failed to fetch user profile:", error);
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API}/login`, `username=${username}&password=${password}`, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      localStorage.setItem('token', response.data.access_token);
      await fetchUserProfile(response.data.access_token);
      return { success: true };
    } catch (error) {
      console.error("Login failed:", error);
      return { success: false, message: error.response?.data?.detail || "Login failed" };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const register = async (email, username, password) => {
    try {
      await axios.post(`${API}/users`, {
        email,
        username,
        password
      });
      // Auto login after registration
      return await login(username, password);
    } catch (error) {
      console.error("Registration failed:", error);
      return { success: false, message: error.response?.data?.detail || "Registration failed" };
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
}

function useAuth() {
  return useContext(AuthContext);
}

// Components
function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="bg-gray-900 text-white py-4">
      <div className="container mx-auto flex justify-between items-center px-4">
        <Link to="/" className="text-xl font-bold">StockNewsScanner</Link>
        <div className="space-x-4 flex items-center">
          <Link to="/" className="hover:text-blue-400">News</Link>
          <Link to="/stocks" className="hover:text-blue-400">Stocks</Link>
          <Link to="/forum" className="hover:text-blue-400">Forum</Link>
          {user ? (
            <div className="flex items-center space-x-4">
              <Link to="/profile" className="hover:text-blue-400">{user.username}</Link>
              <button onClick={handleLogout} className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded">Logout</button>
            </div>
          ) : (
            <div className="space-x-2">
              <Link to="/login" className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded">Login</Link>
              <Link to="/register" className="bg-green-600 hover:bg-green-700 px-3 py-1 rounded">Register</Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

function NewsCard({ news }) {
  return (
    <Link to={`/news/${news.id}`} className="block hover:no-underline">
      <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden transition-transform hover:scale-105 hover:shadow-xl">
        <div className="p-6">
          <div className="flex justify-between items-start">
            <h3 className="text-xl font-bold text-white mb-2">{news.title}</h3>
            <div className="flex items-center bg-blue-600 text-white text-xs font-semibold rounded-full px-2 py-1">
              {news.confidence_score.toFixed(2)} confidence
            </div>
          </div>
          <p className="text-gray-300 mb-4">{news.content}</p>
          <div className="flex flex-wrap gap-2 mb-4">
            {news.affected_stocks.map(stock => (
              <span 
                key={stock}
                className="bg-indigo-600 text-white px-2 py-1 rounded text-sm"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  window.location.href = `/stocks/${stock}`;
                }}
              >
                {stock}
              </span>
            ))}
          </div>
          <div className="flex justify-between items-center text-sm text-gray-400">
            <span>Source: {news.source}</span>
            <span>{formatDate(news.published_at)}</span>
          </div>
          <div className="mt-4 text-sm text-gray-400">
            <span>Validated by: {news.validated_sources.join(', ')}</span>
          </div>
        </div>
      </div>
    </Link>
  );
}

function Home() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  
  useEffect(() => {
    fetchNews();
  }, [selectedCategory]);
  
  const fetchNews = async () => {
    try {
      setLoading(true);
      const url = selectedCategory 
        ? `${API}/news?category=${selectedCategory}` 
        : `${API}/news`;
      const response = await axios.get(url);
      setNews(response.data);
      
      // Get unique categories from news
      if (!selectedCategory) {
        const uniqueCategories = [...new Set(response.data.map(item => item.category))];
        setCategories(uniqueCategories);
      }
    } catch (err) {
      console.error("Error fetching news:", err);
      setError("Failed to load news. Please try again later.");
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Latest Market News</h1>
        <p className="text-gray-300">Stay updated with news that moves markets</p>
      </div>
      
      {/* Category Filter */}
      <div className="mb-6 flex flex-wrap gap-2">
        <button
          className={`px-3 py-1 rounded ${!selectedCategory ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'}`}
          onClick={() => setSelectedCategory(null)}
        >
          All
        </button>
        {categories.map(category => (
          <button
            key={category}
            className={`px-3 py-1 rounded ${selectedCategory === category ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'}`}
            onClick={() => setSelectedCategory(category)}
          >
            {category}
          </button>
        ))}
      </div>
      
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-600 text-white p-4 rounded">
          {error}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {news.map(item => (
            <NewsCard key={item.id} news={item} />
          ))}
        </div>
      )}
    </div>
  );
}

function NewsDetail() {
  const { newsId } = useParams();
  const [news, setNews] = useState(null);
  const [impacts, setImpacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    fetchNewsDetail();
  }, [newsId]);
  
  const fetchNewsDetail = async () => {
    try {
      setLoading(true);
      const newsResponse = await axios.get(`${API}/news/${newsId}`);
      setNews(newsResponse.data);
      
      const impactsResponse = await axios.get(`${API}/news/${newsId}/impacts`);
      setImpacts(impactsResponse.data);
    } catch (err) {
      console.error("Error fetching news detail:", err);
      setError("Failed to load news details. Please try again later.");
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }
  
  if (error || !news) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-600 text-white p-4 rounded">
          {error || "News not found"}
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-4">
        <Link to="/" className="text-blue-500 hover:underline">&larr; Back to News</Link>
      </div>
      
      <div className="bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
        <h1 className="text-2xl font-bold text-white mb-4">{news.title}</h1>
        <div className="flex items-center gap-2 mb-4">
          <span className="bg-blue-600 text-white px-2 py-1 rounded-full text-sm">
            {news.confidence_score.toFixed(2)} confidence
          </span>
          <span className="bg-indigo-600 text-white px-2 py-1 rounded-full text-sm">
            {news.category}
          </span>
        </div>
        <p className="text-gray-300 mb-6">{news.content}</p>
        <div className="flex flex-wrap gap-2 mb-4">
          {news.affected_stocks.map(stock => (
            <Link 
              key={stock} 
              to={`/stocks/${stock}`}
              className="bg-indigo-600 text-white px-3 py-1 rounded"
            >
              {stock}
            </Link>
          ))}
        </div>
        <div className="flex justify-between items-center text-sm text-gray-400">
          <span>Source: {news.source}</span>
          <a href={news.url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
            Original Article
          </a>
          <span>{formatDate(news.published_at)}</span>
        </div>
        <div className="mt-4 text-sm text-gray-400">
          <span>Validated by: {news.validated_sources.join(', ')}</span>
        </div>
      </div>
      
      <h2 className="text-xl font-bold text-white mb-4">Stock Impacts</h2>
      
      {impacts.length === 0 ? (
        <p className="text-gray-300">No impact analysis available for this news item.</p>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {impacts.map(impact => (
            <div key={impact.id} className={`p-4 rounded-lg border-l-4 ${impact.impact_score > 0 ? 'border-green-500 bg-green-900 bg-opacity-20' : 'border-red-500 bg-red-900 bg-opacity-20'}`}>
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-lg font-semibold text-white">
                  Impact on Stock {impact.stock_id}
                </h3>
                <span className={`font-bold ${impact.impact_score > 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {impact.impact_score > 0 ? '+' : ''}{impact.impact_score.toFixed(2)}
                </span>
              </div>
              <p className="text-gray-300">{impact.explanation}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function StocksList() {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [exchanges, setExchanges] = useState([]);
  const [selectedExchange, setSelectedExchange] = useState(null);
  
  useEffect(() => {
    fetchStocks();
  }, [selectedExchange]);
  
  const fetchStocks = async () => {
    try {
      setLoading(true);
      const url = selectedExchange 
        ? `${API}/stocks?exchange=${selectedExchange}` 
        : `${API}/stocks`;
      const response = await axios.get(url);
      setStocks(response.data);
      
      // Get unique exchanges
      if (!selectedExchange) {
        const uniqueExchanges = [...new Set(response.data.map(stock => stock.exchange))];
        setExchanges(uniqueExchanges);
      }
    } catch (err) {
      console.error("Error fetching stocks:", err);
      setError("Failed to load stocks. Please try again later.");
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Stocks</h1>
        <p className="text-gray-300">View all stocks and their recent news</p>
      </div>
      
      {/* Exchange Filter */}
      <div className="mb-6 flex flex-wrap gap-2">
        <button
          className={`px-3 py-1 rounded ${!selectedExchange ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'}`}
          onClick={() => setSelectedExchange(null)}
        >
          All Exchanges
        </button>
        {exchanges.map(exchange => (
          <button
            key={exchange}
            className={`px-3 py-1 rounded ${selectedExchange === exchange ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'}`}
            onClick={() => setSelectedExchange(exchange)}
          >
            {exchange}
          </button>
        ))}
      </div>
      
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-600 text-white p-4 rounded">
          {error}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {stocks.map(stock => (
            <Link key={stock.id} to={`/stocks/${stock.symbol}`} className="block">
              <div className="bg-gray-800 rounded-lg p-4 hover:bg-gray-700 transition-colors">
                <div className="flex justify-between items-center">
                  <h3 className="text-xl font-bold text-white">{stock.symbol}</h3>
                  <span className="text-gray-400 text-sm">{stock.exchange}</span>
                </div>
                <p className="text-gray-300 mt-2">{stock.name}</p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

function StockDetail() {
  const { stockId } = useParams();
  const [stock, setStock] = useState(null);
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user } = useAuth();
  const [isFavorite, setIsFavorite] = useState(false);
  
  useEffect(() => {
    if (stockId) {
      fetchStockDetail();
    }
  }, [stockId]);
  
  useEffect(() => {
    if (user && stock) {
      setIsFavorite(user.favorite_stocks.includes(stock.symbol));
    }
  }, [user, stock]);
  
  const fetchStockDetail = async () => {
    try {
      setLoading(true);
      console.log(`Fetching stock details for: ${stockId}`);
      const stockResponse = await axios.get(`${API}/stocks/${stockId}`);
      setStock(stockResponse.data);
      
      const newsResponse = await axios.get(`${API}/stocks/${stockId}/news`);
      setNews(newsResponse.data);
    } catch (err) {
      console.error("Error fetching stock detail:", err);
      setError("Failed to load stock details. Please try again later.");
    } finally {
      setLoading(false);
    }
  };
  
  const toggleFavorite = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('token');
      if (isFavorite) {
        await axios.delete(`${API}/users/me/favorite-stocks/${stock.symbol}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        await axios.post(`${API}/users/me/favorite-stocks/${stock.symbol}`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      setIsFavorite(!isFavorite);
    } catch (err) {
      console.error("Error updating favorites:", err);
    }
  };
  
  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }
  
  if (error || !stock) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-600 text-white p-4 rounded">
          {error || "Stock not found"}
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-4">
        <Link to="/stocks" className="text-blue-500 hover:underline">&larr; Back to Stocks</Link>
      </div>
      
      <div className="bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">{stock.symbol}</h1>
            <h2 className="text-xl text-gray-300 mb-4">{stock.name}</h2>
            <div className="bg-indigo-600 inline-block text-white px-3 py-1 rounded">
              {stock.exchange}
            </div>
          </div>
          {user && (
            <button
              onClick={toggleFavorite}
              className={`p-2 rounded-full ${isFavorite ? 'bg-yellow-500 text-white' : 'bg-gray-700 text-gray-300'}`}
            >
              {isFavorite ? '★' : '☆'}
            </button>
          )}
        </div>
      </div>
      
      <h2 className="text-xl font-bold text-white mb-4">Recent News</h2>
      
      {news.length === 0 ? (
        <p className="text-gray-300">No recent news found for this stock.</p>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {news.map(item => (
            <NewsCard key={item.id} news={item} />
          ))}
        </div>
      )}
    </div>
  );
}

function ForumList() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user } = useAuth();
  const navigate = useNavigate();
  
  useEffect(() => {
    fetchPosts();
  }, []);
  
  const fetchPosts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/forum/posts`);
      setPosts(response.data);
    } catch (err) {
      console.error("Error fetching forum posts:", err);
      setError("Failed to load forum posts. Please try again later.");
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Community Forum</h1>
          <p className="text-gray-300">Discuss trading strategies and market insights</p>
        </div>
        {user && (
          <button
            onClick={() => navigate('/forum/new')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
          >
            New Post
          </button>
        )}
      </div>
      
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-600 text-white p-4 rounded">
          {error}
        </div>
      ) : (
        <div className="space-y-6">
          {posts.length === 0 ? (
            <p className="text-gray-300">No forum posts yet. Be the first to start a discussion!</p>
          ) : (
            posts.map(post => (
              <div key={post.id} className="bg-gray-800 rounded-lg shadow-lg p-6">
                <Link to={`/forum/${post.id}`} className="block hover:no-underline">
                  <h2 className="text-xl font-bold text-white mb-2 hover:text-blue-400">{post.title}</h2>
                </Link>
                <p className="text-gray-300 mb-4">{post.content.length > 150 ? post.content.substring(0, 150) + '...' : post.content}</p>
                
                <div className="flex flex-wrap gap-2 mb-4">
                  {post.stocks.map(stock => (
                    <Link 
                      key={stock} 
                      to={`/stocks/${stock}`}
                      className="bg-indigo-600 text-white px-2 py-1 rounded text-sm"
                    >
                      {stock}
                    </Link>
                  ))}
                </div>
                
                <div className="flex justify-between items-center text-sm text-gray-400">
                  <span>By: {post.username}</span>
                  <div className="flex items-center gap-4">
                    <span>Comments: {post.comments.length}</span>
                    <span className="flex items-center">
                      <svg className="w-4 h-4 mr-1 text-yellow-500" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                      </svg>
                      {post.upvotes}
                    </span>
                  </div>
                  <span>{formatDate(post.created_at)}</span>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

function NewForumPost() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [stocks, setStocks] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    if (!user) {
      navigate('/login');
    }
  }, [user, navigate]);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!title.trim() || !content.trim()) {
      setError('Title and content are required');
      return;
    }
    
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const stocksArray = stocks
        .split(',')
        .map(s => s.trim())
        .filter(s => s);
      
      await axios.post(
        `${API}/forum/posts`,
        {
          title,
          content,
          stocks: stocksArray
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      navigate('/forum');
    } catch (err) {
      console.error("Error creating forum post:", err);
      setError("Failed to create post. Please try again later.");
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-4">
        <Link to="/forum" className="text-blue-500 hover:underline">&larr; Back to Forum</Link>
      </div>
      
      <div className="bg-gray-800 rounded-lg shadow-lg p-6">
        <h1 className="text-2xl font-bold text-white mb-6">Create New Post</h1>
        
        {error && (
          <div className="bg-red-600 text-white p-4 rounded mb-4">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="title" className="block text-gray-300 mb-2">Title</label>
            <input
              type="text"
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-gray-700 text-white border border-gray-600 rounded py-2 px-3 focus:outline-none focus:border-blue-500"
              placeholder="Post title"
              required
            />
          </div>
          
          <div className="mb-4">
            <label htmlFor="content" className="block text-gray-300 mb-2">Content</label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="w-full bg-gray-700 text-white border border-gray-600 rounded py-2 px-3 focus:outline-none focus:border-blue-500 h-40"
              placeholder="Share your insights or strategy..."
              required
            ></textarea>
          </div>
          
          <div className="mb-6">
            <label htmlFor="stocks" className="block text-gray-300 mb-2">Related Stocks (comma-separated)</label>
            <input
              type="text"
              id="stocks"
              value={stocks}
              onChange={(e) => setStocks(e.target.value)}
              className="w-full bg-gray-700 text-white border border-gray-600 rounded py-2 px-3 focus:outline-none focus:border-blue-500"
              placeholder="AAPL, MSFT, GOOGL"
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center"
          >
            {loading && (
              <div className="animate-spin mr-2 h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
            )}
            Create Post
          </button>
        </form>
      </div>
    </div>
  );
}

function ForumPostDetail() {
  const { postId } = useParams();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [commenting, setCommenting] = useState(false);
  const [error, setError] = useState(null);
  const { user } = useAuth();
  
  useEffect(() => {
    fetchPostDetail();
  }, [postId]);
  
  const fetchPostDetail = async () => {
    try {
      setLoading(true);
      const postResponse = await axios.get(`${API}/forum/posts/${postId}`);
      setPost(postResponse.data);
      
      const commentsResponse = await axios.get(`${API}/forum/posts/${postId}/comments`);
      setComments(commentsResponse.data);
    } catch (err) {
      console.error("Error fetching post detail:", err);
      setError("Failed to load post details. Please try again later.");
    } finally {
      setLoading(false);
    }
  };
  
  const upvotePost = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/forum/posts/${postId}/upvote`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update local state
      setPost(prev => ({
        ...prev,
        upvotes: prev.upvotes + 1
      }));
    } catch (err) {
      console.error("Error upvoting post:", err);
    }
  };
  
  const addComment = async (e) => {
    e.preventDefault();
    if (!user || !newComment.trim()) return;
    
    try {
      setCommenting(true);
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/forum/posts/${postId}/comments`,
        { content: newComment },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setComments(prev => [...prev, response.data]);
      setNewComment('');
    } catch (err) {
      console.error("Error adding comment:", err);
      setError("Failed to add comment. Please try again.");
    } finally {
      setCommenting(false);
    }
  };
  
  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }
  
  if (error || !post) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-600 text-white p-4 rounded">
          {error || "Post not found"}
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-4">
        <Link to="/forum" className="text-blue-500 hover:underline">&larr; Back to Forum</Link>
      </div>
      
      <div className="bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
        <div className="flex justify-between items-start mb-4">
          <h1 className="text-2xl font-bold text-white">{post.title}</h1>
          {user && (
            <button
              onClick={upvotePost}
              className="flex items-center gap-1 bg-gray-700 hover:bg-gray-600 text-white px-3 py-1 rounded"
            >
              <svg className="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
              </svg>
              {post.upvotes}
            </button>
          )}
        </div>
        
        <p className="text-gray-300 mb-6 whitespace-pre-line">{post.content}</p>
        
        <div className="flex flex-wrap gap-2 mb-4">
          {post.stocks.map(stock => (
            <Link 
              key={stock} 
              to={`/stocks/${stock}`}
              className="bg-indigo-600 text-white px-2 py-1 rounded text-sm"
            >
              {stock}
            </Link>
          ))}
        </div>
        
        <div className="flex justify-between items-center text-sm text-gray-400">
          <span>By: {post.username}</span>
          <span>{formatDate(post.created_at)}</span>
        </div>
      </div>
      
      <h2 className="text-xl font-bold text-white mb-4">Comments ({comments.length})</h2>
      
      {user && (
        <div className="bg-gray-800 rounded-lg p-4 mb-6">
          <form onSubmit={addComment}>
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              className="w-full bg-gray-700 text-white border border-gray-600 rounded py-2 px-3 focus:outline-none focus:border-blue-500 h-24 mb-3"
              placeholder="Add your comment..."
              required
            ></textarea>
            
            <button
              type="submit"
              disabled={commenting || !newComment.trim()}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center"
            >
              {commenting && (
                <div className="animate-spin mr-2 h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
              )}
              Post Comment
            </button>
          </form>
        </div>
      )}
      
      {comments.length === 0 ? (
        <p className="text-gray-300">No comments yet. Be the first to share your thoughts!</p>
      ) : (
        <div className="space-y-4">
          {comments.map(comment => (
            <div key={comment.id} className="bg-gray-800 rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <span className="font-medium text-white">{comment.username}</span>
                <span className="text-sm text-gray-400">{formatDate(comment.created_at)}</span>
              </div>
              <p className="text-gray-300">{comment.content}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    try {
      const result = await login(username, password);
      if (result.success) {
        navigate('/');
      } else {
        setError(result.message);
      }
    } catch (err) {
      console.error("Login error:", err);
      setError("An unexpected error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8 max-w-md">
      <div className="bg-gray-800 rounded-lg shadow-lg p-6">
        <h1 className="text-2xl font-bold text-white mb-6 text-center">Log In</h1>
        
        {error && (
          <div className="bg-red-600 text-white p-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="username" className="block text-gray-300 mb-2">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-gray-700 text-white border border-gray-600 rounded py-2 px-3 focus:outline-none focus:border-blue-500"
              placeholder="Your username"
              required
            />
          </div>
          
          <div className="mb-6">
            <label htmlFor="password" className="block text-gray-300 mb-2">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-gray-700 text-white border border-gray-600 rounded py-2 px-3 focus:outline-none focus:border-blue-500"
              placeholder="Your password"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded flex justify-center items-center"
          >
            {loading && (
              <div className="animate-spin mr-2 h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
            )}
            Log In
          </button>
        </form>
        
        <div className="mt-4 text-center text-gray-400">
          Don't have an account? <Link to="/register" className="text-blue-500 hover:underline">Register</Link>
        </div>
      </div>
    </div>
  );
}

function Register() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    try {
      const result = await register(email, username, password);
      if (result.success) {
        navigate('/');
      } else {
        setError(result.message);
      }
    } catch (err) {
      console.error("Registration error:", err);
      setError("An unexpected error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8 max-w-md">
      <div className="bg-gray-800 rounded-lg shadow-lg p-6">
        <h1 className="text-2xl font-bold text-white mb-6 text-center">Create Account</h1>
        
        {error && (
          <div className="bg-red-600 text-white p-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="email" className="block text-gray-300 mb-2">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-gray-700 text-white border border-gray-600 rounded py-2 px-3 focus:outline-none focus:border-blue-500"
              placeholder="Your email"
              required
            />
          </div>
          
          <div className="mb-4">
            <label htmlFor="username" className="block text-gray-300 mb-2">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-gray-700 text-white border border-gray-600 rounded py-2 px-3 focus:outline-none focus:border-blue-500"
              placeholder="Choose a username"
              required
            />
          </div>
          
          <div className="mb-6">
            <label htmlFor="password" className="block text-gray-300 mb-2">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-gray-700 text-white border border-gray-600 rounded py-2 px-3 focus:outline-none focus:border-blue-500"
              placeholder="Choose a password"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded flex justify-center items-center"
          >
            {loading && (
              <div className="animate-spin mr-2 h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
            )}
            Register
          </button>
        </form>
        
        <div className="mt-4 text-center text-gray-400">
          Already have an account? <Link to="/login" className="text-blue-500 hover:underline">Log In</Link>
        </div>
      </div>
    </div>
  );
}

function UserProfile() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [favoriteStocks, setFavoriteStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    
    fetchFavoriteStocks();
  }, [user, navigate]);
  
  const fetchFavoriteStocks = async () => {
    try {
      setLoading(true);
      
      if (!user || !user.favorite_stocks.length) {
        setFavoriteStocks([]);
        return;
      }
      
      const stocksData = [];
      for (const symbol of user.favorite_stocks) {
        try {
          const response = await axios.get(`${API}/stocks/${symbol}`);
          stocksData.push(response.data);
        } catch (err) {
          console.error(`Error fetching stock ${symbol}:`, err);
        }
      }
      
      setFavoriteStocks(stocksData);
    } catch (err) {
      console.error("Error fetching favorite stocks:", err);
    } finally {
      setLoading(false);
    }
  };
  
  if (!user) return null;
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
        <h1 className="text-2xl font-bold text-white mb-4">Your Profile</h1>
        <p className="text-gray-300 mb-2"><span className="font-semibold">Username:</span> {user.username}</p>
        <p className="text-gray-300"><span className="font-semibold">Email:</span> {user.email}</p>
      </div>
      
      <div className="mb-8">
        <h2 className="text-xl font-bold text-white mb-4">Favorite Stocks</h2>
        
        {loading ? (
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : favoriteStocks.length === 0 ? (
          <p className="text-gray-300">You haven't added any favorite stocks yet.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {favoriteStocks.map(stock => (
              <Link key={stock.id} to={`/stocks/${stock.symbol}`} className="block">
                <div className="bg-gray-800 rounded-lg p-4 hover:bg-gray-700 transition-colors">
                  <div className="flex justify-between items-center">
                    <h3 className="text-xl font-bold text-white">{stock.symbol}</h3>
                    <span className="text-gray-400 text-sm">{stock.exchange}</span>
                  </div>
                  <p className="text-gray-300 mt-2">{stock.name}</p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App min-h-screen bg-gray-900 text-white">
          <Navbar />
          <main>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/news/:newsId" element={<NewsDetail />} />
              <Route path="/stocks" element={<StocksList />} />
              <Route path="/stocks/:stockId" element={<StockDetail />} />
              <Route path="/forum" element={<ForumList />} />
              <Route path="/forum/new" element={<NewForumPost />} />
              <Route path="/forum/:postId" element={<ForumPostDetail />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/profile" element={<UserProfile />} />
            </Routes>
          </main>
          <footer className="mt-12 py-6 text-center text-gray-500">
            <p>&copy; {new Date().getFullYear()} StockNewsScanner. All rights reserved.</p>
          </footer>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
