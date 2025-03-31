from dotenv import load_dotenv
import unittest
from unittest.mock import patch, MagicMock
import json
import os
from .tool import SearchGoogleOfficial, ToolException

load_dotenv()

class TestSearchGoogleOfficial(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.api_key = "test_api_key"
        self.search_engine_id = "test_cx_id"
        self.tool = SearchGoogleOfficial(
            api_key=self.api_key,
            search_engine_id=self.search_engine_id
        )

    def test_initialization(self):
        """Test tool initialization with direct parameters"""
        self.assertEqual(self.tool.api_key, self.api_key)
        self.assertEqual(self.tool.search_engine_id, self.search_engine_id)

    def test_initialization_with_env_vars(self):
        """Test tool initialization with environment variables"""
        with patch.dict(os.environ, {
            'GOOGLE_SEARCH_API_KEY': 'env_api_key',
            'GOOGLE_CX_ID': 'env_cx_id'
        }):
            tool = SearchGoogleOfficial()
            self.assertEqual(tool.api_key, 'env_api_key')
            self.assertEqual(tool.search_engine_id, 'env_cx_id')

    def test_initialization_without_credentials(self):
        """Test tool initialization without credentials"""
        with patch.dict(os.environ, clear=True):
            with self.assertRaises(ValueError):
                SearchGoogleOfficial()

    @patch('requests.Session.get')
    def test_successful_search(self, mock_get):
        """Test successful search request"""
        # Mock response data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [{
                "title": "Test Title",
                "link": "https://test.com",
                "snippet": "Test snippet",
                "displayLink": "test.com",
                "formattedUrl": "https://test.com"
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Execute search
        result = self.tool._run(query="test query", num=1)
        result_dict = json.loads(result)

        # Verify results
        self.assertIn("items", result_dict)
        self.assertEqual(len(result_dict["items"]), 1)
        self.assertEqual(result_dict["items"][0]["title"], "Test Title")

    @patch('requests.Session.get')
    def test_search_with_error(self, mock_get):
        """Test search with API error"""
        mock_get.side_effect = ToolException("API Error")
        
        result = self.tool._run(query="test query")
        result_dict = json.loads(result)
        
        self.assertIn("error", result_dict)
        self.assertTrue(result_dict["error"].startswith("搜索执行失败"))

    def test_invalid_num_parameter(self):
        """Test handling of invalid num parameter"""
        with patch.object(self.tool, '_make_request') as mock_request:
            mock_request.return_value = {"items": []}
            
            # Test with num > 10
            result = self.tool._run(query="test", num=15)
            result_dict = json.loads(result)
            self.assertIn("items", result_dict)
            
            # Test with num < 1
            result = self.tool._run(query="test", num=0)
            result_dict = json.loads(result)
            self.assertIn("items", result_dict)

    def test_missing_query_parameter(self):
        """Test search without query parameter"""
        result = self.tool._run(num=5)
        result_dict = json.loads(result)
        
        self.assertIn("error", result_dict)
        self.assertEqual(result_dict["error"], "必须提供搜索关键词")

class TestSearchGoogleOfficialIntegration(unittest.TestCase):
    """Integration tests that perform real Google searches"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment for all integration tests"""
        # Check if we have the required environment variables
        cls.api_key = os.environ.get('GOOGLE_SEARCH_API_KEY')
        cls.search_engine_id = os.environ.get('GOOGLE_CX_ID')
        if not cls.api_key or not cls.search_engine_id:
            raise unittest.SkipTest(
                "Skipping integration tests: GOOGLE_SEARCH_API_KEY and GOOGLE_CX_ID "
                "environment variables are required for integration tests"
            )
        cls.tool = SearchGoogleOfficial(
            api_key=cls.api_key,
            search_engine_id=cls.search_engine_id
        )

    def test_real_search(self):
        """Test performing a real Google search"""
        # Execute a real search
        result = self.tool._run(
            query="Python programming language official website",
            num=3
        )
        result_dict = json.loads(result)

        # Verify the structure and basic content of the response
        self.assertIn("items", result_dict)
        
        # Verify we got the expected number of results
        self.assertEqual(len(result_dict["items"]), 3)
        
        # Verify each result has the required fields
        for result in result_dict["items"]:
            self.assertIn("title", result)
            self.assertIn("link", result)
            self.assertIn("snippet", result)
            self.assertIn("displayLink", result)
            
            # Verify the URLs are valid
            self.assertTrue(result["link"].startswith("http"))
            
            # Verify we have non-empty content
            self.assertTrue(len(result["title"]) > 0)
            self.assertTrue(len(result["snippet"]) > 0)

    def test_real_search_with_filters(self):
        """Test performing a real Google search with various filters"""
        # Execute a search with multiple parameters
        result = self.tool._run(
            query="Python tutorial",
            num=2,
            dateRestrict="y1",  # Last year
            lr="lang_en",       # English results only
            fileType="pdf"      # PDF files only
        )
        result_dict = json.loads(result)

        # Verify we got results
        self.assertIn("items", result_dict)
        self.assertTrue(len(result_dict["items"]) > 0)
        
        # Verify PDF files in results
        for result in result_dict["items"]:
            self.assertTrue(
                result["link"].lower().endswith('.pdf') or 
                'pdf' in result["link"].lower()
            )

    def test_real_search_with_site_restriction(self):
        """Test performing a real Google search with site restriction"""
        # Search specifically on python.org
        result = self.tool._run(
            query="getting started tutorial",
            num=2,
            siteSearch="python.org",
            siteSearchFilter="i"  # include only python.org
        )
        result_dict = json.loads(result)

        # Verify results are from python.org
        self.assertIn("items", result_dict)
        for result in result_dict["items"]:
            self.assertTrue(
                "python.org" in result["link"].lower() or
                "python.org" in result["displayLink"].lower()
            )

if __name__ == '__main__':
    unittest.main()
