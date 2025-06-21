from src.main import app
import logging

logging.basicConfig(
    level=logging.DEBUG,  # Troque para logging.INFO caso deseje menos verbosidade
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)