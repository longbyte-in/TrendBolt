#!/usr/bin/env python3
"""
TrendBolt MCP Server with Simple Logging
This script runs the MCP server with minimal logging that won't interfere with MCP protocol
"""

import os
import sys
import logging
from pathlib import Path

# Set up minimal logging that won't interfere with MCP protocol
log_level = os.getenv('TRENDBOLT_LOG_LEVEL', 'INFO')
log_file = os.getenv('TRENDBOLT_LOG_FILE', 'trendbolt.log')

# Configure logging to file only (not stdout to avoid MCP interference)
logging.basicConfig(
    level=getattr(logging, log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Run the MCP server with logging."""
    logger.info("Starting TrendBolt MCP Server with logging...")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Log file: {log_file}")
    
    try:
        # Import and run the server
        from trendbolt_mcp.server import main as server_main
        logger.info("Server imported successfully")
        await server_main()
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
