# state.py
import asyncio

# Global state variables
shutting_down = False
shutdown_lock = asyncio.Lock()