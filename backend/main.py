from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def root():
    return {"status": "Backend is live"}

# Input model
class HealthInput(BaseModel):
    age: int
    bmi: float
    sleep_hours: float
    activity_minutes: int
    stress_level: int
    screen_time: float

# AI risk calculation
def calculate_risk(data: HealthInput) -> str:
    score = 0
    if data.sleep_hours < 6:
        score += 2
    if data.activity_minutes < 30:
        score += 2
    if data.stress_level > 6:
        score += 2
    if data.screen_time > 6:
        score += 2
    if data.bmi > 25:
        score += 2

    if score <= 3:
        return "Low"
    elif score <= 6:
        return "Medium"
    else:
        return "High"

# Main endpoint
@app.post("/assess")
def assess_health(data: HealthInput):
    risk = calculate_risk(data)

    try:
        conn = psycopg2.connect(
            os.getenv("DATABASE_URL"),
            connect_timeout=5
        )
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO health_checkins
            (age, bmi, sleep_hours, activity_minutes, stress_level, screen_time, risk_level)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                data.age,
                data.bmi,
                data.sleep_hours,
                data.activity_minutes,
                data.stress_level,
                data.screen_time,
                risk
            )
        )

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print("DB Error:", e)

    return {
        "risk_level": risk,
        "recommendation": (
            "Maintain healthy habits"
            if risk == "Low"
            else "Improve lifestyle balance"
        )
    }
