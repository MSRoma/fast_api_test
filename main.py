import re
from ipaddress import ip_address
from typing import Callable
from pathlib import Path

import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db

#from src.routes import contacts, auth, users
from src.config.config import config


app = FastAPI()

banned_ips = [
    ip_address("192.168.1.1"),
    ip_address("192.168.1.2"),
    ip_address("127.0.0.1"),
]

# ALLOWED_IPS = [
#     ip_address('192.168.1.0'),
#     ip_address('172.16.0.0'),
#     ip_address("127.0.0.1"),
#     ]


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.middleware("http")
# async def limit_access_by_ip(request: Request, call_next: Callable):
#     ip = ip_address(request.client.host)
#     if ip not in ALLOWED_IPS:
#         return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Not allowed IP address"})
#     response = await call_next(request)
#     return response


# @app.middleware("http")
# async def ban_ips(request: Request, call_next: Callable):
#     ip = ip_address(request.client.host)
#     if ip in banned_ips:
#         return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
#     response = await call_next(request)
#     return response

user_agent_ban_list = [r"Googlebot", r"Python-urllib"]


# @app.middleware("http")
# async def user_agent_ban_middleware(request: Request, call_next: Callable):
#     print(request.headers.get("Authorization"))
#     user_agent = request.headers.get("user-agent")
#     print(user_agent)
#     for ban_pattern in user_agent_ban_list:
#         if re.search(ban_pattern, user_agent):
#             return JSONResponse(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 content={"detail": "You are banned"},
#             )
#     response = await call_next(request)
#     return response

# BASE_DIR = Path(__file__).parent

# directory = BASE_DIR.joinpath("src").joinpath("static")
# app.mount("/static", StaticFiles(directory=directory), name="static")

# app.include_router(auth.router, prefix='/api')
# app.include_router(users.router, prefix="/api")
# app.include_router(contacts.router, prefix='/api')


# app.include_router(tags.router, prefix='/api')
# app.include_router(notes.router, prefix='/api')


@app.get("/")
def read_root():
    return {"message": "Hello World"}

# @app.on_event("startup")
# async def startup():

#     r = await redis.Redis(
#         host=config.REDIS_DOMAIN,
#         port=config.REDIS_PORT,
#         db=0,
#         password=config.REDIS_PASSWORD,
#     )
#     await FastAPILimiter.init(r)

@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Healthchecker.

    :param db: The database session.
    :type db: Session
    :return: Message: "Welcome to FastAPI!".
    :rtype: str
    """
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")