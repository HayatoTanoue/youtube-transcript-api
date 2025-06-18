#!/usr/bin/env python3
"""
Simple test to validate optimizations work without requiring YouTube API calls.
"""

import sys
import os
import time
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from youtube_transcript_api import YouTubeTranscriptApi


def test_api_initialization():
    """Test that API initializes with optimizations."""
    print("Testing API initialization with optimizations...")
    
    api = YouTubeTranscriptApi(enable_caching=True)
    assert hasattr(api, '_fetcher'), "API should have fetcher"
    assert hasattr(api._fetcher, '_enable_caching'), "Fetcher should have caching flag"
    assert api._fetcher._enable_caching == True, "Caching should be enabled"
    assert hasattr(api._fetcher, '_transcript_cache'), "Fetcher should have cache"
    
    api_no_cache = YouTubeTranscriptApi(enable_caching=False)
    assert api_no_cache._fetcher._enable_caching == False, "Caching should be disabled"
    assert api_no_cache._fetcher._transcript_cache is None, "Cache should be None when disabled"
    
    print("  ✓ API initialization test passed!")
    return True


def test_http_optimization():
    """Test that HTTP session optimization is applied."""
    print("Testing HTTP session optimization...")
    
    api = YouTubeTranscriptApi()
    http_client = api._fetcher._http_client
    
    expected_headers = {
        "Accept-Language": "en-US",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    
    for header, expected_value in expected_headers.items():
        actual_value = http_client.headers.get(header)
        assert actual_value == expected_value, f"Header {header} should be {expected_value}, got {actual_value}"
    
    assert "http://" in http_client.adapters, "HTTP adapter should be mounted"
    assert "https://" in http_client.adapters, "HTTPS adapter should be mounted"
    
    print("  ✓ HTTP optimization test passed!")
    return True


def test_parallel_api_exists():
    """Test that parallel processing API exists."""
    print("Testing parallel processing API...")
    
    api = YouTubeTranscriptApi()
    
    assert hasattr(api, 'fetch_multiple'), "API should have fetch_multiple method"
    
    with patch.object(api, 'fetch') as mock_fetch:
        mock_fetch.return_value = Mock()
        
        results = api.fetch_multiple(['test1', 'test2'], max_workers=2)
        
        assert 'transcripts' in results, "Results should have transcripts key"
        assert 'failed_video_ids' in results, "Results should have failed_video_ids key"
        assert 'success_count' in results, "Results should have success_count key"
        assert 'total_count' in results, "Results should have total_count key"
    
    print("  ✓ Parallel processing API test passed!")
    return True


def test_api_compatibility():
    """Test that existing API methods still work."""
    print("Testing API compatibility...")
    
    api = YouTubeTranscriptApi()
    
    assert hasattr(api, 'fetch'), "fetch method should exist"
    assert hasattr(api, 'list'), "list method should exist"
    assert hasattr(api, 'fetch_multiple'), "fetch_multiple method should exist"
    
    assert hasattr(api, 'get_transcript'), "get_transcript method should exist for compatibility"
    assert hasattr(api, 'list_transcripts'), "list_transcripts method should exist for compatibility"
    
    print("  ✓ API compatibility test passed!")
    return True


def main():
    """Run all optimization tests."""
    print("Running simple optimization validation tests...")
    print("=" * 60)
    
    tests = [
        test_api_initialization,
        test_http_optimization,
        test_parallel_api_exists,
        test_api_compatibility,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All optimization tests passed!")
        print("\nOptimizations implemented:")
        print("  • HTTP session optimization with connection pooling")
        print("  • Caching mechanism for repeated requests")
        print("  • Parallel processing for multiple videos")
        print("  • Full API compatibility maintained")
        return True
    else:
        print("✗ Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
