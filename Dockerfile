FROM python:3.13-slim
WORKDIR /app
RUN apt-get update \
    && apt-get install --no-install-recommends -y make \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir uv==0.8.14
COPY pyproject.toml uv.lock README.md ./
COPY fieldforge fieldforge
RUN uv sync --locked --no-dev
ENV PATH="/app/.venv/bin:$PATH"
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "dashboard/app.py", "--server.address=0.0.0.0"]
