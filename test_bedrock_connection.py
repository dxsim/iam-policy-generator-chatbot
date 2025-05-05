import os
import json
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_bedrock_connection():
    """
    Test the connection to AWS Bedrock using the credentials in the .env file.
    This script helps verify that your AWS credentials are correctly configured
    before running the main application.
    """
    print("Testing connection to AWS Bedrock...")
    
    try:
        # Initialize Bedrock client
        client = boto3.client(
            service_name="bedrock-runtime",
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY")
        )
        
        # Test model ID
        model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        
        # Simple test prompt
        test_prompt = "What are AWS IAM policies?"
        
        # Invoke model with a simple prompt
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "system": "You are a helpful assistant.",
                "messages": [
                    {
                        "role": "user",
                        "content": test_prompt
                    }
                ]
            })
        )
        
        # Parse response
        response_body = json.loads(response.get('body').read().decode('utf-8'))
        response_text = response_body['content'][0]['text']
        
        print("\n✅ Connection successful! Received response from Bedrock:")
        print("-" * 50)
        print(response_text[:200] + "..." if len(response_text) > 200 else response_text)
        print("-" * 50)
        print("\nYour AWS credentials are correctly configured.")
        print("You can now run the main application with: python app.py")
        
    except Exception as e:
        print("\n❌ Connection failed with error:")
        print("-" * 50)
        print(str(e))
        print("-" * 50)
        print("\nPlease check your:")
        print("1. AWS credentials in the .env file")
        print("2. AWS region (make sure Bedrock is available in your selected region)")
        print("3. Network connectivity")
        print("4. AWS IAM permissions (ensure your user/role has bedrock:InvokeModel permission)")

if __name__ == "__main__":
    test_bedrock_connection()
