"""Central Loguru configuration with rotation and retention.

Applications may replace the sink in one place to integrate with a managed
logging platform. Never log passwords, bearer tokens, or reset links.
"""

from loguru import logger

logger.remove()
logger.add("logs/app.log", rotation="10 MB", retention="30 days", serialize=True, enqueue=True)
logger.add(lambda message: print(message, end=""), level="INFO")
