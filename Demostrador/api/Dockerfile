FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.8.0 \
    && pip install --no-cache-dir -r requirements.txt

COPY main.py database.py schemas.py examples_TB_con_resumen.jsonl ./
COPY a5_runtime.py a5_drive.py a5_alignment.py a5_providers.py prompt_v11_1_snapshot.json ./

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
