#!/bin/bash

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "UV is not installed. Please install UV first."
    echo "You can install it using: curl -sSf https://install.ultraviolet.rs | sh"
    exit 1
fi

# Set up virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Setting up virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies using UV
echo "Installing dependencies with UV from pyproject.toml..."
uv pip install -e .

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    
    echo "Enter your OpenAI API key:"
    read OPENAI_API_KEY
    
    echo "Enter your Tavily API key:"
    read TAVILY_API_KEY
    
    echo "OPENAI_API_KEY=$OPENAI_API_KEY" > .env
    echo "TAVILY_API_KEY=$TAVILY_API_KEY" >> .env
    
    echo ".env file created successfully!"
fi

# Run the application with chainlit
echo "Starting the Research Agent with Chainlit..."
chainlit run app.py -w 