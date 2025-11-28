from main import app

if __name__ == '__main__':
    import uvicorn
    print("✓ Swagger UI available at: http://localhost:8000/docs")
    uvicorn.run(app, host='0.0.0.0', port=8000)