import os
import json
import gradio as gr
import boto3
import re
from dotenv import load_dotenv
from policy_validator import PolicyValidator
from policy_utils import PolicyUtils

# Load environment variables
load_dotenv()

# Initialize utilities
policy_validator = PolicyValidator()
policy_utils = PolicyUtils()

# Initialize Bedrock client
def get_bedrock_client():
    return boto3.client(
        service_name="bedrock-runtime",
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY")
    )

# Model ID for Claude 3.5 Sonnet
MODEL_ID = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"

# Function to generate IAM policy using Claude
def generate_iam_policy(prompt, client):
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

# Extract policy JSON from text
def extract_policy_json(text):
    try:
        # Look for JSON content between triple backticks
        json_pattern = r"```json\s*([\s\S]*?)\s*```"
        match = re.search(json_pattern, text)
        
        if match:
            json_str = match.group(1).strip()
            # Validate it's proper JSON
            policy = json.loads(json_str)
            return json_str, policy
        
        # Alternative: look for content that looks like JSON
        json_pattern = r"\{\s*\"Version\"[\s\S]*?\"Statement\"[\s\S]*?\}"
        match = re.search(json_pattern, text)
        
        if match:
            json_str = match.group(0).strip()
            # Validate it's proper JSON
            policy = json.loads(json_str)
            return json_str, policy
                
        return None, None
    except:
        return None, None

# Validate policy and format results
def validate_policy_from_text(text):
    json_str, policy = extract_policy_json(text)
    
    if not policy:
        return "No valid policy found in the response."
    
    # Validate the policy
    validation_results = policy_validator.validate_policy(policy)
    
    # Format the results
    result = "## Policy Validation Results\n\n"
    
    if validation_results["valid"]:
        result += "✅ **Policy is valid according to best practices.**\n\n"
    else:
        result += "⚠️ **Policy has some issues to address:**\n\n"
        
    if validation_results["issues"]:
        result += "### Issues:\n"
        for issue in validation_results["issues"]:
            result += f"- {issue}\n"
        result += "\n"
    
    if validation_results["recommendations"]:
        result += "### Recommendations:\n"
        for rec in validation_results["recommendations"]:
            result += f"- {rec}\n"
    
    return result

# Save policy to file
def save_policy_from_text(text, policy_name=None):
    success, result = policy_utils.extract_and_save_policy(text, policy_name)
    
    if success:
        return f"✅ Policy saved successfully to: {result}"
    else:
        return f"❌ Failed to save policy: {result}"

# Chat history and state management
def add_text(history, text):
    history = history + [(text, None)]
    return history, ""

def bot_response(history, client_state):
    if not history:
        return history, client_state, None, None
    
    user_message = history[-1][0]
    
    # Get or create Bedrock client
    if client_state is None:
        try:
            client_state = get_bedrock_client()
        except Exception as e:
            history[-1][1] = f"Error connecting to AWS Bedrock: {str(e)}"
            return history, client_state, None, None
    
    # Generate response
    response = generate_iam_policy(user_message, client_state)
    history[-1][1] = response
    
    # Extract and validate policy
    validation_result = validate_policy_from_text(response)
    
    # Extract policy JSON for display
    json_str, _ = extract_policy_json(response)
    policy_json = json_str if json_str else "No valid policy JSON found in the response."
    
    return history, client_state, validation_result, policy_json

def save_current_policy(policy_json, policy_name):
    if not policy_json or policy_json == "No valid policy JSON found in the response.":
        return "No valid policy to save."
    
    return save_policy_from_text(policy_json, policy_name)

# List saved policies
def list_policies():
    policies = policy_utils.list_saved_policies()
    
    if not policies:
        return "No saved policies found."
    
    result = "## Saved Policies\n\n"
    for policy in policies:
        result += f"- {policy}\n"
    
    return result

# Create Gradio interface
with gr.Blocks(title="AWS IAM Policy Generator") as demo:
    gr.Markdown("# AWS IAM Minimum Viable Permissions Generator")
    gr.Markdown("""
    This tool helps AWS cloud administrators generate minimum viable IAM permissions based on specific use cases.
    """)
    
    # Store states
    client_state = gr.State(None)
    current_policy_json = gr.State(None)
    
    with gr.Tabs() as tabs:
        with gr.TabItem("Generate Policy"):
            gr.Markdown("""
            **How to use:**
            1. Describe your AWS use case in detail
            2. The system will generate a minimal IAM policy with explanations
            3. Review the policy and reasoning before implementation
            
            **Example prompt:** "I need permissions for an EC2 instance to read from a specific S3 bucket named 'company-data' and write logs to CloudWatch."
            """)
            
            chatbot = gr.Chatbot(
                [],
                elem_id="chatbot",
                bubble_full_width=False,
                height=500,
                avatar_images=(None, "🤖"),
            )
            
            with gr.Row():
                txt = gr.Textbox(
                    scale=4,
                    show_label=False,
                    placeholder="Describe your AWS use case here...",
                    container=False,
                )
                submit_btn = gr.Button("Generate Policy", scale=1)
            
            with gr.Accordion("Policy Validation", open=False):
                validation_output = gr.Markdown()
            
            with gr.Accordion("Policy JSON", open=False):
                policy_json_output = gr.Code(language="json")
            
            with gr.Row():
                policy_name_input = gr.Textbox(
                    label="Policy Name (optional)",
                    placeholder="Enter a name for this policy",
                )
                save_btn = gr.Button("Save Policy")
            
            save_result = gr.Markdown()
            
        with gr.TabItem("Saved Policies"):
            refresh_btn = gr.Button("Refresh List")
            saved_policies_output = gr.Markdown()
    
    # Event handlers
    txt.submit(add_text, [chatbot, txt], [chatbot, txt]).then(
        bot_response, [chatbot, client_state], [chatbot, client_state, validation_output, policy_json_output]
    )
    submit_btn.click(add_text, [chatbot, txt], [chatbot, txt]).then(
        bot_response, [chatbot, client_state], [chatbot, client_state, validation_output, policy_json_output]
    )
    save_btn.click(save_current_policy, [policy_json_output, policy_name_input], save_result)
    refresh_btn.click(list_policies, [], saved_policies_output)
    
    gr.Markdown("""
    ### Important Notes:
    - Always review generated policies before implementation
    - The generated policies follow the principle of least privilege
    - Consider additional security measures like conditions and MFA requirements
    - This tool is meant to assist administrators, not replace human review
    """)

if __name__ == "__main__":
    demo.launch(share=True)
