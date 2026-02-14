FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY truststack_grc ./truststack_grc
COPY pyproject.toml .

# Mounts
RUN mkdir -p /app/registry /app/workspaces

EXPOSE 8000
CMD ["uvicorn", "truststack_grc.main:app", "--host", "0.0.0.0", "--port", "8000"]
