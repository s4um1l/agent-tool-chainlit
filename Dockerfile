# Get a distribution that has uv already installed
FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

# Add Rust compiler installation for dependencies that might need it
USER root
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Add user - this is the user that will run the app
RUN useradd -m -u 1000 user
USER user

# Set up Rust for the user
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/home/user/.cargo/bin:${PATH}"

# Set the home directory and path
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH        

# Set Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/home/user/app \
    UVICORN_WS_PROTOCOL=websockets

# Set the working directory
WORKDIR $HOME/app

# First copy all files needed for dependency installation
COPY --chown=user pyproject.toml $HOME/app/
COPY --chown=user README.md $HOME/app/
# Create src directory
RUN mkdir -p $HOME/app/src

# Copy dependencies first
COPY --chown=user requirements.txt* $HOME/app/


# Now copy the rest of the application (improves Docker build caching)
COPY --chown=user . $HOME/app/

# Create required directories for Chainlit
RUN mkdir -p $HOME/app/.chainlit
RUN mkdir -p $HOME/.cache

# Install application with uv sync again after all files are present
RUN uv sync

# Create .env file from environment variables at runtime
RUN echo "#!/bin/bash" > $HOME/app/entrypoint.sh && \
    echo "# Create .env file from environment variables" >> $HOME/app/entrypoint.sh && \
    echo "if [ ! -f .env ]; then" >> $HOME/app/entrypoint.sh && \
    echo '    echo "OPENAI_API_KEY=$OPENAI_API_KEY" > .env' >> $HOME/app/entrypoint.sh && \
    echo '    echo "TAVILY_API_KEY=$TAVILY_API_KEY" >> .env' >> $HOME/app/entrypoint.sh && \
    echo "fi" >> $HOME/app/entrypoint.sh && \
    echo "# Run the application" >> $HOME/app/entrypoint.sh && \
    echo 'uv run chainlit run app.py --host "0.0.0.0" --port "7860"' >> $HOME/app/entrypoint.sh && \
    chmod +x $HOME/app/entrypoint.sh

# Expose the port
EXPOSE 7860

# Run the app using the entrypoint script
CMD ["./entrypoint.sh"]