#!/bin/bash
# IAM Policy Generator Setup and Run Script
# This script helps users set up and run the IAM Policy Generator application

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== AWS IAM Policy Generator Setup ===${NC}"

# Check if Python is installed
echo -e "\n${YELLOW}Checking Python installation...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
    echo -e "${GREEN}Python 3 is installed.${NC}"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
    echo -e "${GREEN}Python is installed.${NC}"
else
    echo -e "${RED}Error: Python is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "Python version: $PYTHON_VERSION"

# Check if pip is installed
echo -e "\n${YELLOW}Checking pip installation...${NC}"
if command -v pip3 &>/dev/null; then
    PIP_CMD="pip3"
    echo -e "${GREEN}pip3 is installed.${NC}"
elif command -v pip &>/dev/null; then
    PIP_CMD="pip"
    echo -e "${GREEN}pip is installed.${NC}"
else
    echo -e "${RED}Error: pip is not installed. Please install pip.${NC}"
    exit 1
fi

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
$PIP_CMD install -r requirements.txt
echo -e "${GREEN}Dependencies installed successfully.${NC}"

# Check if .env file exists
echo -e "\n${YELLOW}Checking for .env file...${NC}"
if [ -f .env ]; then
    echo -e "${GREEN}.env file exists.${NC}"
else
    echo -e "${YELLOW}.env file not found. Creating from template...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}.env file created from example.${NC}"
        echo -e "${YELLOW}Please edit the .env file with your AWS credentials before running the application.${NC}"
        
        # Open the .env file in the default editor if possible
        if command -v nano &>/dev/null; then
            echo -e "Opening .env file with nano..."
            nano .env
        elif command -v vim &>/dev/null; then
            echo -e "Opening .env file with vim..."
            vim .env
        else
            echo -e "${YELLOW}Please edit the .env file with your preferred text editor.${NC}"
        fi
    else
        echo -e "${RED}Error: .env.example file not found.${NC}"
        exit 1
    fi
fi

# Create saved_policies directory if it doesn't exist
echo -e "\n${YELLOW}Setting up directories...${NC}"
mkdir -p saved_policies
echo -e "${GREEN}Directory structure ready.${NC}"

# Test Bedrock connection
echo -e "\n${YELLOW}Testing connection to AWS Bedrock...${NC}"
echo -e "${YELLOW}(This step is optional. Press Ctrl+C to skip if you want to configure AWS credentials later)${NC}"
echo -e "Running test_bedrock_connection.py..."
$PYTHON_CMD test_bedrock_connection.py || {
    echo -e "\n${YELLOW}AWS Bedrock connection test failed.${NC}"
    echo -e "${YELLOW}Please check your AWS credentials in the .env file.${NC}"
    echo -e "${YELLOW}You can still run the application, but it may not work correctly until credentials are configured.${NC}"
}

# Ask user what they want to do
echo -e "\n${BLUE}=== What would you like to do? ===${NC}"
echo -e "1. Run the web application (Gradio interface)"
echo -e "2. Generate a policy from the command line"
echo -e "3. View saved policies"
echo -e "4. Exit"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo -e "\n${YELLOW}Starting the web application...${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop the application.${NC}"
        $PYTHON_CMD app.py
        ;;
    2)
        echo -e "\n${YELLOW}Running the command-line policy generator...${NC}"
        read -p "Enter your AWS use case description: " use_case
        $PYTHON_CMD generate_policy_cli.py "$use_case"
        ;;
    3)
        echo -e "\n${YELLOW}Listing saved policies...${NC}"
        $PYTHON_CMD view_policy.py list
        
        # If there are saved policies, ask if user wants to view one
        if [ $? -eq 0 ]; then
            read -p "Enter the name of a policy to view (or press Enter to skip): " policy_name
            if [ ! -z "$policy_name" ]; then
                $PYTHON_CMD view_policy.py view "$policy_name"
            fi
        fi
        ;;
    4)
        echo -e "\n${GREEN}Exiting. Goodbye!${NC}"
        exit 0
        ;;
    *)
        echo -e "\n${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}Done!${NC}"
