import uvicorn


if __name__ == "__main__":
    uvicorn.run("ai_messenger_voicemail.app:app", host="0.0.0.0", port=8000, reload=True)
