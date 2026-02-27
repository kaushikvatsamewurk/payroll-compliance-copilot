#!/bin/bash

uvicorn app:app --host 0.0.0.0 --port 8000 &

streamlit run ui.py --server.port 10000 --server.address 0.0.0.0