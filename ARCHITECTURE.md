# IAM Policy Generator Architecture

This document provides an overview of the IAM Policy Generator's architecture, explaining how the different components work together.

## System Overview

The IAM Policy Generator is a tool that helps AWS administrators create minimum viable IAM policies based on natural language descriptions of use cases. It uses Amazon Bedrock's Claude 3.5 Sonnet model to generate policies that follow the principle of least privilege.

![System Architecture](https://mermaid.ink/img/pako:eNp1kk1PwzAMhv9KlBMgTVu7dRvigJA4cEFCHBBCVeamWZQ2VT4QMPHfcbuxMcTpZT-P_dpODtBYjZCBdXpnNlYRfCjTWLKkNPCu3JvQkjOtgZvWOUtw0Yg3ZQm-jKmIYE3wqpxtCT6Vd4JXJCqChdlTQ_ChnPcEr9o0dYRXZbdE8GZcTfDc-I7gVe8qgkflHeHFmJ3gxdTKE3xY1xK8WtsRnI3rCFZm3xHMxjUEi3YNQW1cTVAZXxFUxtcEtXE1wdK4muDJuIZgNq4leNK-JXhUviV4Ur4jmI3vCGrjO4LK-J6gNL4nKE3oCUrjA0FpQiAoTQgECxMCwcKEQFCYEAgKEwLBwoRAsDChJ1iY0BMUJvQEhQk9QWFCIChMGAjmJgwEcxMGgrkJA8HMhIFgZsJAMDNhIJiZEAlmJkSCmQmRYGZCJJiZEAlmJkSCmQmRYGZCJJiZkAhmJiSCmQmJYGZCIpiZkAhmJiSCmQmJYGZCIpiZkAhmJmSCmQmZYGZCJpiZkAlmJmSCmQmZYGZCJpiZkAlmJmSCmQmFYGZCIZiZUAhmJhSCmQmFYGZCIZiZUAhmJhSCmQmFYGZCJZiZUAlmJlSCmQmVYGZCJZiZUAlmJlSCmQmVYGZCJZiZsBDMTFgIZiYsBDMTFoKZCQvBzISFYGbCQjAzYSGYmbAQzExYCWYmrAQzE1aCmQkrwcyElWBmwkowM2ElmJmwEsxMWAlmJmwEMxM2gpkJG8HMhI1gZsJGMDNhI5iZsBHMTNgIZiZsBDMTdoKZCTvBzISdYGbCTjAzYSeYmbATzEzYCWYm7AQzE3aCmQkHwcyEg2BmwkEwM-EgmJlwEMxMOAhmJhwEMxMOgpkJB8HMhJNgZsJJMDPhJJiZcBLMTDgJZiacBDMTToKZCSfBzISTYGbCRTAz4SKYmXARzEy4CGYmXAQzEy6CmQkXwcyEi2BmwkUwM-EmmJlwE8xMuAlmJtwEMxNugpkJN8HMhJtgZsJNMDPhJpiZ8BDMTL4BxYkZlQ?type=png)

## Components

### 1. User Interface (Gradio)

The user interface is built using Gradio, a Python library for creating web interfaces for machine learning models. It provides:

- A chat interface for users to describe their AWS use cases
- Display of generated policies with explanations
- Policy validation results
- Ability to save policies for future reference

**Key Files:**
- `app.py`: Main application file that sets up the Gradio interface

### 2. Policy Generation (Amazon Bedrock)

The policy generation component uses Amazon Bedrock's Claude 3.5 Sonnet model to generate IAM policies based on natural language descriptions. It:

- Formats prompts with specific instructions for the model
- Sends requests to the Bedrock API
- Processes and extracts the generated policies from the responses

**Key Files:**
- `app.py`: Contains the `generate_iam_policy` function
- `generate_policy_cli.py`: Command-line interface for policy generation

### 3. Policy Validation

The policy validation component checks generated policies against IAM best practices and provides recommendations for improvement. It:

- Identifies overly permissive actions (e.g., wildcards)
- Checks for missing resource constraints
- Validates policy structure
- Provides recommendations for improvement

**Key Files:**
- `policy_validator.py`: Contains the `PolicyValidator` class
- `test_policy_validator.py`: Tests for the validator

### 4. Policy Management

The policy management component handles saving, loading, and managing generated policies. It:

- Saves policies to JSON files with metadata
- Lists saved policies
- Loads policies for viewing or validation

**Key Files:**
- `policy_utils.py`: Contains the `PolicyUtils` class
- `view_policy.py`: Command-line interface for viewing saved policies

### 5. Command-line Tools

The application includes several command-line tools for users who prefer working in the terminal:

- `generate_policy_cli.py`: Generate policies from the command line
- `view_policy.py`: View and validate saved policies
- `test_policy_validator.py`: Test the policy validator
- `test_bedrock_connection.py`: Test the connection to AWS Bedrock
- `setup_and_run.sh`: Set up and run the application

## Data Flow

1. **User Input**: The user describes their AWS use case in natural language through the Gradio interface or command-line tool.

2. **Policy Generation**: The description is sent to the Bedrock API, which generates an IAM policy with explanations.

3. **Policy Validation**: The generated policy is validated against best practices, and issues are identified.

4. **Display Results**: The policy, explanations, and validation results are displayed to the user.

5. **Policy Management**: The user can save the policy for future reference or make adjustments based on validation results.

## Configuration

The application uses environment variables for configuration, stored in a `.env` file:

- `AWS_ACCESS_KEY_ID`: AWS access key for Bedrock API access
- `AWS_SECRET_ACCESS_KEY`: AWS secret key for Bedrock API access
- `AWS_REGION`: AWS region where Bedrock is available

## Directory Structure

```
iam-policy-generator-chatbot/
├── app.py                           # Main application file
├── policy_validator.py              # Policy validation module
├── policy_utils.py                  # Policy management utilities
├── generate_policy_cli.py           # CLI for policy generation
├── view_policy.py                   # CLI for viewing policies
├── test_policy_validator.py         # Tests for policy validator
├── test_bedrock_connection.py       # Test AWS Bedrock connection
├── setup_and_run.sh                 # Setup and run script
├── requirements.txt                 # Python dependencies
├── .env.example                     # Example environment variables
├── .gitignore                       # Git ignore file
├── README.md                        # Project documentation
├── ARCHITECTURE.md                  # Architecture documentation
├── saved_policies/                  # Directory for saved policies
└── example_policies/                # Example policy files
    ├── s3_read_only.json
    └── lambda_dynamodb_cloudwatch.json
```

## Extension Points

The application is designed to be easily extended:

1. **Custom Validators**: Add new validation rules to `policy_validator.py`
2. **Additional Models**: Support for other LLMs by modifying the `generate_iam_policy` function
3. **New Features**: Add new tabs to the Gradio interface in `app.py`
4. **Integration**: Use `generate_policy_cli.py` as a library in other applications
