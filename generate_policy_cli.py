#!/usr/bin/env python3
"""
IAM Policy Generator CLI

This script demonstrates how to use the IAM policy generator programmatically.
It allows users to generate IAM policies from the command line without using the Gradio interface.

Usage:
  python generate_policy_cli.py "I need permissions for an EC2 instance to read from an S3 bucket named 'data-bucket'"
  python generate_policy_cli.py --file use_case.txt
  python generate_policy_cli.py --save my_policy "I need permissions for a Lambda to access DynamoDB"
"""

import os
import sys
import json
import argparse
import boto3
from dotenv import load_dotenv
from policy_validator import PolicyValidator
from policy_utils import PolicyUtils

# Load environment variables
load_dotenv()

def get_bedrock_client():
    """Initialize and return a Bedrock client"""
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY")
    )

def generate_iam_policy(prompt, client):
    """Generate an IAM policy using the Bedrock Claude model"""
    MODEL_ID = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    
    system_prompt = """
    You are an AWS IAM policy expert assistant. Your task is to generate minimum viable permission (MVP) 
    IAM policies based on the user's description of their AWS use case.
    
    Follow these guidelines:
    1. Analyze the user's request carefully to understand their specific AWS use case
    2. Generate the most restrictive IAM policy that still allows all necessary operations
    3. Follow the principle of least privilege
    4. Include only the permissions that are absolutely necessary
    5. Use resource-level restrictions whenever possible
    6. Provide clear explanations for why each permission is included
    7. Format the policy according to AWS IAM JSON syntax
    8. Highlight any potential security concerns or recommendations
    
    Your response should include:
    1. A summary of your understanding of the use case
    2. The complete IAM policy in JSON format (enclosed in ```json and ``` markers)
    3. A detailed explanation of each permission and why it's necessary
    4. Any security recommendations or best practices relevant to this use case
    
    IMPORTANT: Always format the policy JSON with proper indentation and enclose it in ```json and ``` markers
    to make it easy to extract.
    """
    
    try:
        response = client.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(response.get('body').read().decode('utf-8'))
        return response_body['content'][0]['text']
    except Exception as e:
        return f"Error generating IAM policy: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Generate AWS IAM policies from the command line")
    
    # Define mutually exclusive group for input source
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("prompt", nargs="?", help="Use case description for policy generation")
    input_group.add_argument("--file", help="File containing the use case description")
    
    # Other arguments
    parser.add_argument("--save", metavar="NAME", help="Save the generated policy with the specified name")
    parser.add_argument("--validate", action="store_true", help="Validate the generated policy")
    parser.add_argument("--json-only", action="store_true", help="Output only the JSON policy")
    
    args = parser.parse_args()
    
    # Get the prompt from either command line or file
    if args.prompt:
        prompt = args.prompt
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                prompt = f.read().strip()
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            sys.exit(1)
    
    # Initialize utilities
    policy_utils = PolicyUtils()
    policy_validator = PolicyValidator()
    
    try:
        # Get Bedrock client
        client = get_bedrock_client()
        
        # Generate policy
        print("Generating IAM policy... (this may take a moment)")
        response = generate_iam_policy(prompt, client)
        
        # Extract policy JSON
        json_str, policy = policy_utils.extract_policy_from_text(response)
        
        if not json_str:
            print("Error: Could not extract a valid policy from the response.")
            print("\nFull response:")
            print(response)
            sys.exit(1)
        
        # Output based on options
        if args.json_only:
            print(json.dumps(policy, indent=2))
        else:
            print(response)
        
        # Validate if requested
        if args.validate:
            validation_results = policy_validator.validate_policy(policy)
            
            print("\n=== Policy Validation Results ===")
            
            if validation_results["valid"]:
                print("✅ Policy is valid according to best practices.")
            else:
                print("⚠️ Policy has some issues to address:")
            
            if validation_results["issues"]:
                print("\nIssues:")
                for issue in validation_results["issues"]:
                    print(f"- {issue}")
            
            if validation_results["recommendations"]:
                print("\nRecommendations:")
                for rec in validation_results["recommendations"]:
                    print(f"- {rec}")
        
        # Save if requested
        if args.save:
            filepath = policy_utils.save_policy(json_str, args.save, f"Policy generated from: {prompt[:50]}...")
            if filepath:
                print(f"\nPolicy saved to: {filepath}")
            else:
                print("\nError: Failed to save policy.")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
