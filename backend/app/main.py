# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import employees, customers, orders, auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # port dev server frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router)
app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(auth.router)

