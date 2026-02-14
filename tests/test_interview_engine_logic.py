
import sys
import os
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock database settings before importing engine
with patch('backend.config.settings') as mock_settings:
    mock_settings.openai_api_key = "dummy"
    mock_settings.openrouter_base_url = "dummy"
    mock_settings.llm_model = "dummy"
    
    from backend.services.interview_engine import generate_reply

async def test_retry_logic():
    print("--- Testing Retry Logic ---")
    
    with patch('backend.services.interview_engine._get_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        
        # Scenario: First attempt empty, second attempt success
        mock_response_empty = MagicMock()
        mock_response_empty.choices[0].message.content = ""
        
        mock_response_success = MagicMock()
        mock_response_success.choices[0].message.content = "Better response without dashes"
        
        mock_client.chat.completions.create.side_effect = [mock_response_empty, mock_response_success]
        
        result = await generate_reply([], 0)
        print(f"Result: {result}")
        
        if result['reply'] == "Better response without dashes":
            print("✅ Retry success")
        else:
            print("❌ Retry failed")
            
async def test_em_dash_removal():
    print("\n--- Testing Em-Dash Removal ---")
    
    with patch('backend.services.interview_engine._get_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "I hear you — this is a test — right?"
        
        mock_client.chat.completions.create.return_value = mock_response
        
        result = await generate_reply([], 0)
        print(f"Result: {result}")
        
        if "—" not in result['reply'] and ", " in result['reply']:
            print("✅ Em-dash removed")
        else:
            print(f"❌ Em-dash removal failed: {result['reply']}")

def main():
    asyncio.run(test_retry_logic())
    asyncio.run(test_em_dash_removal())

if __name__ == "__main__":
    main()
