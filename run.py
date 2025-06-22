from src.main import app
import logging
import uvicorn

logging.basicConfig(
    level=logging.DEBUG,  # Troque para logging.INFO caso deseje menos verbosidade
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)
