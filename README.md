# IAM Policy Generator Chatbot

A Gradio-based chatbot that generates Minimum Viable Permissions (MVP) AWS IAM policies based on natural language descriptions of use cases. This tool helps AWS cloud administrators quickly create least-privilege IAM policies without the need for extensive manual policy crafting.

## Features

- Interactive chat interface built with Gradio
- Powered by Amazon Bedrock's Claude 3.5 Sonnet model
- Generates IAM policies following the principle of least privilege
- Provides detailed explanations for each permission
- Includes security recommendations and best practices

## Prerequisites

- Python 3.8+
- AWS account with access to Amazon Bedrock
- AWS credentials with permissions to invoke Bedrock models

## Installation

### UV installation (Recommended)

If your server has the uv package, you should use this:

```bash
# In case you do not have python 3.13 under UV:
uv python install 3.13
# Or to install a version that satisfies constraints:
uv python install '>=3.12,<=3.13'

# Then download uv dependencies
uv init 
uv python pin 3.13
uv add -r requirements.txt
```


### Quick Setup through Script

Use the provided setup script to quickly get started:

```bash
# Clone the repository
git clone https://github.com/yourusername/iam-policy-generator-chatbot.git
cd iam-policy-generator-chatbot

# Make the setup script executable
chmod +x setup_and_run.sh

# Run the setup script
./setup_and_run.sh
```

The setup script will:
1. Check for Python and pip installation
2. Install required dependencies
3. Create a `.env` file if it doesn't exist
4. Test the connection to AWS Bedrock
5. Provide options to run the web application, generate policies from the command line, or view saved policies

### Manual Setup

If you prefer to set up manually:

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/iam-policy-generator-chatbot.git
   cd iam-policy-generator-chatbot
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on the provided `.env.example`:
   ```
   cp .env.example .env
   ```

4. Edit the `.env` file with your AWS credentials:
   ```
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   AWS_REGION=us-east-1  # Change to your preferred region where Bedrock is available
   ```

5. Create the directory for saved policies:
   ```
   mkdir -p saved_policies
   ```

## Usage

### Web Interface

1. Run the application:
   ```
   python app.py
   ```

2. Open the provided URL in your web browser (typically http://127.0.0.1:7860)

3. Enter a description of your AWS use case in the text box and click "Generate Policy"

4. Review the generated policy and explanations before implementation

5. Use the validation results to identify potential security issues

6. Save policies for future reference

### Command Line

Generate policies directly from the command line:

```bash
# Generate a policy
./generate_policy_cli.py "I need permissions for an EC2 instance to read from an S3 bucket"

# View saved policies
./view_policy.py list
```

## Features

### Policy Generation
- Interactive chat interface for describing AWS use cases
- Detailed explanations of each permission included in the policy
- Follows the principle of least privilege

### Policy Validation
- Automatic validation against IAM best practices
- Identifies overly permissive permissions
- Flags missing resource constraints
- Provides recommendations for improvement

### Policy Management
- Save generated policies with custom names
- View saved policies in the application
- Export policies as JSON files

## Architecture

For a detailed overview of the system architecture and how the components work together, see [ARCHITECTURE.md](ARCHITECTURE.md).

### Command-line Tools

#### Policy Viewer
View and analyze saved policies:
```
# List all saved policies
uv run view_policy.py list

# View a specific policy
uv run view_policy.py view policy_name.json

# Validate a policy against best practices
uv run view_policy.py validate policy_name.json
```

#### Policy Generator CLI
Generate policies directly from the command line without using the web interface:
```
# Generate a policy from a text description
uv run generate_policy_cli.py "I need permissions for an EC2 instance to read from an S3 bucket named 'data-bucket'"

# Generate a policy from a description in a file
uv run generate_policy_cli.py --file use_case.txt

# Generate, validate, and save a policy
uv run generate_policy_cli.py --validate --save my_policy "I need permissions for a Lambda to access DynamoDB"

# Output only the JSON policy
uv run generate_policy_cli.py --json-only "Provide this user athena read only access to a table named 'test_table' under database named 'dev'"
```

## Example Prompts

- "I need permissions for an EC2 instance to read from a specific S3 bucket named 'company-data' and write logs to CloudWatch."
- "Create a policy for a Lambda function that needs to access items from a DynamoDB table called 'user-profiles' and send emails via SES."
- "I need a policy for a developer role that can deploy CloudFormation stacks but only in the development account."
- "Generate permissions for a CI/CD pipeline that needs to deploy to ECS and update a CloudFront distribution."

## Example Policies

The `example_policies` directory contains reference IAM policies that demonstrate best practices:

- `s3_read_only.json`: Read-only access to a specific S3 bucket with condition constraints
- `lambda_dynamodb_cloudwatch.json`: Permissions for a Lambda function to read from DynamoDB and write logs to CloudWatch

## Security Considerations

- Always review generated policies before implementation
- Consider adding conditions to further restrict permissions
- Implement additional security controls like MFA where appropriate
- Regularly audit and rotate credentials
- Use resource-level permissions whenever possible
- Avoid wildcard permissions in production environments

## License
[LICENSE](LICENSE)
