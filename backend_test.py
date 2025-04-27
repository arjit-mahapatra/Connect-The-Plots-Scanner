import requests
import sys
import uuid
import logging
from datetime import datetime
import random
import string

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialNewsAPITester:
    def __init__(self, base_url="https://3105c4f6-f875-4fb4-a7b2-8d66c5684cd2.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user = None
        self.test_password = None
        self.test_email = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        logger.info(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                logger.info(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                logger.error(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    logger.error(f"Error details: {error_detail}")
                except:
                    logger.error(f"Response text: {response.text}")
                return success, {}

        except Exception as e:
            logger.error(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def generate_test_user(self):
        """Generate a unique test user"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = ''.join(random.choices(string.ascii_lowercase, k=5))
        self.test_user = f"testuser_{timestamp}_{random_str}"
        self.test_password = f"TestPass_{random_str}123!"
        self.test_email = f"{self.test_user}@example.com"
        return self.test_user, self.test_password, self.test_email

    def test_register_user(self):
        """Test user registration"""
        if not self.test_user:
            self.generate_test_user()
            
        success, response = self.run_test(
            "User Registration",
            "POST",
            "users",
            200,
            data={"username": self.test_user, "password": self.test_password, "email": self.test_email}
        )
        return success

    def test_login(self):
        """Test login and get token"""
        success, response = self.run_test(
            "Login",
            "POST",
            "login",
            200,
            data={"username": self.test_user, "password": self.test_password}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True
        return False

    def test_get_user_profile(self):
        """Test getting the current user profile"""
        success, response = self.run_test(
            "Get User Profile",
            "GET",
            "users/me",
            200
        )
        return success

    def test_get_news(self):
        """Test getting news items"""
        success, response = self.run_test(
            "Get News Items",
            "GET",
            "news",
            200
        )
        logger.info(f"Retrieved {len(response)} news items")
        return success, response

    def test_get_stocks(self):
        """Test getting stocks"""
        success, response = self.run_test(
            "Get Stocks",
            "GET",
            "stocks",
            200
        )
        logger.info(f"Retrieved {len(response)} stocks")
        return success, response

    def test_get_stock_by_id(self, stock_id):
        """Test getting a stock by ID"""
        success, response = self.run_test(
            f"Get Stock by ID: {stock_id}",
            "GET",
            f"stocks/{stock_id}",
            200
        )
        if success:
            logger.info(f"Stock details: {response['symbol']} - {response['name']}")
        return success, response

    def test_get_stock_news(self, stock_id):
        """Test getting news for a specific stock"""
        success, response = self.run_test(
            f"Get News for Stock: {stock_id}",
            "GET",
            f"stocks/{stock_id}/news",
            200
        )
        if success:
            logger.info(f"Retrieved {len(response)} news items for stock {stock_id}")
        return success, response

    def test_get_news_detail(self, news_id):
        """Test getting news detail"""
        success, response = self.run_test(
            f"Get News Detail: {news_id}",
            "GET",
            f"news/{news_id}",
            200
        )
        if success:
            logger.info(f"News title: {response['title']}")
        return success, response

    def test_get_news_impacts(self, news_id):
        """Test getting news impacts"""
        success, response = self.run_test(
            f"Get News Impacts: {news_id}",
            "GET",
            f"news/{news_id}/impacts",
            200
        )
        if success:
            logger.info(f"Retrieved {len(response)} impact records for news {news_id}")
        return success, response

    def test_add_favorite_stock(self, stock_id):
        """Test adding a stock to favorites"""
        success, response = self.run_test(
            f"Add Stock to Favorites: {stock_id}",
            "POST",
            f"users/me/favorite-stocks/{stock_id}",
            200
        )
        return success, response

    def test_remove_favorite_stock(self, stock_id):
        """Test removing a stock from favorites"""
        success, response = self.run_test(
            f"Remove Stock from Favorites: {stock_id}",
            "DELETE",
            f"users/me/favorite-stocks/{stock_id}",
            200
        )
        return success, response

    def test_get_forum_posts(self):
        """Test getting forum posts"""
        success, response = self.run_test(
            "Get Forum Posts",
            "GET",
            "forum/posts",
            200
        )
        if success:
            logger.info(f"Retrieved {len(response)} forum posts")
        return success, response

    def test_get_forum_post(self, post_id):
        """Test getting a forum post"""
        success, response = self.run_test(
            f"Get Forum Post: {post_id}",
            "GET",
            f"forum/posts/{post_id}",
            200
        )
        if success:
            logger.info(f"Forum post title: {response['title']}")
        return success, response

    def test_get_post_comments(self, post_id):
        """Test getting comments for a post"""
        success, response = self.run_test(
            f"Get Comments for Post: {post_id}",
            "GET",
            f"forum/posts/{post_id}/comments",
            200
        )
        if success:
            logger.info(f"Retrieved {len(response)} comments for post {post_id}")
        return success, response

    def print_results(self):
        """Print test results"""
        logger.info("\n===== TEST RESULTS =====")
        logger.info(f"Total tests run: {self.tests_run}")
        logger.info(f"Tests passed: {self.tests_passed}")
        logger.info(f"Tests failed: {self.tests_run - self.tests_passed}")
        logger.info(f"Success rate: {(self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0:.2f}%")
        logger.info("=======================\n")
        return self.tests_passed == self.tests_run

def main():
    # Get backend URL from args if provided
    if len(sys.argv) > 1:
        backend_url = sys.argv[1]
    else:
        backend_url = "https://3105c4f6-f875-4fb4-a7b2-8d66c5684cd2.preview.emergentagent.com/api"
    
    logger.info(f"Testing against backend URL: {backend_url}")
    
    # Initialize tester
    tester = FinancialNewsAPITester(backend_url)
    
    # Create test user and login
    logger.info("\n===== AUTHENTICATION TESTS =====")
    if not tester.test_register_user():
        logger.error("❌ User registration failed, stopping tests")
        tester.print_results()
        return 1
    
    if not tester.test_login():
        logger.error("❌ Login failed, stopping tests")
        tester.print_results()
        return 1
    
    if not tester.test_get_user_profile():
        logger.error("❌ Getting user profile failed, stopping tests")
        tester.print_results()
        return 1
    
    # Test news endpoints
    logger.info("\n===== NEWS TESTS =====")
    news_success, news_items = tester.test_get_news()
    if not news_success or not news_items:
        logger.error("❌ Failed to get news items, skipping related tests")
    else:
        # Test a specific news item
        if len(news_items) > 0:
            news_item = news_items[0]
            news_id = news_item['id']
            detail_success, _ = tester.test_get_news_detail(news_id)
            if not detail_success:
                logger.warning("⚠️ Failed to get news detail")
            
            impacts_success, _ = tester.test_get_news_impacts(news_id)
            if not impacts_success:
                logger.warning("⚠️ Failed to get news impacts")
    
    # Test stocks endpoints
    logger.info("\n===== STOCKS TESTS =====")
    stocks_success, stocks = tester.test_get_stocks()
    if not stocks_success or not stocks:
        logger.error("❌ Failed to get stocks, skipping related tests")
    else:
        # Test a specific stock
        if len(stocks) > 0:
            stock = stocks[0]
            stock_id = stock['symbol']
            stock_detail_success, _ = tester.test_get_stock_by_id(stock_id)
            if not stock_detail_success:
                logger.warning("⚠️ Failed to get stock detail")
            
            stock_news_success, _ = tester.test_get_stock_news(stock_id)
            if not stock_news_success:
                logger.warning("⚠️ Failed to get stock news")
            
            # Test favorite stocks functionality
            favorite_add_success, _ = tester.test_add_favorite_stock(stock_id)
            if not favorite_add_success:
                logger.warning("⚠️ Failed to add stock to favorites")
            
            favorite_remove_success, _ = tester.test_remove_favorite_stock(stock_id)
            if not favorite_remove_success:
                logger.warning("⚠️ Failed to remove stock from favorites")
    
    # Test forum endpoints
    logger.info("\n===== FORUM TESTS =====")
    forum_success, posts = tester.test_get_forum_posts()
    if not forum_success or not posts:
        logger.error("❌ Failed to get forum posts, skipping related tests")
    else:
        # Test a specific post
        if len(posts) > 0:
            post = posts[0]
            post_id = post['id']
            post_detail_success, _ = tester.test_get_forum_post(post_id)
            if not post_detail_success:
                logger.warning("⚠️ Failed to get post detail")
            
            comments_success, _ = tester.test_get_post_comments(post_id)
            if not comments_success:
                logger.warning("⚠️ Failed to get post comments")
    
    # Print final results
    success = tester.print_results()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())