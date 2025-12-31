"""
Token cleanup utility.
Removes expired tokens from the database to prevent database bloat.
"""
from datetime import datetime, timezone
from app.models.access_token import AccessToken
import logging

logger = logging.getLogger(__name__)

async def cleanup_expired_access_tokens() -> int:
    """
    Remove all expired access tokens from the database.
    Returns the number of tokens deleted.
    """
    try:
        current_time = datetime.now(timezone.utc)
        
        # Get all tokens and check expiration manually to handle timezone issues
        all_tokens = await AccessToken.find().to_list()
        expired_tokens = []
        
        for token in all_tokens:
            expires_at = token.expires_at
            # Handle both timezone-aware and timezone-naive datetimes
            if expires_at.tzinfo is None:
                # If timezone-naive, assume it's UTC
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            
            if expires_at < current_time:
                expired_tokens.append(token)
        
        if not expired_tokens:
            return 0
        
        # Delete expired tokens
        deleted_count = 0
        for token in expired_tokens:
            await token.delete()
            deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} expired access tokens")
        
        return deleted_count
    except Exception as e:
        logger.error(f"Error cleaning up expired tokens: {e}")
        return 0

# Keep old function names for backward compatibility during migration
async def cleanup_expired_tokens() -> int:
    """Alias for cleanup_expired_access_tokens (backward compatibility)."""
    return await cleanup_expired_access_tokens()

async def get_blacklist_stats() -> dict:
    """Alias for get_token_stats (backward compatibility)."""
    return await get_token_stats()

async def get_token_stats() -> dict:
    """
    Get statistics about active tokens.
    Returns count of total tokens and expired tokens.
    """
    try:
        current_time = datetime.now(timezone.utc)
        
        # Get all tokens and check expiration manually to handle timezone issues
        all_tokens = await AccessToken.find().to_list()
        total_count = len(all_tokens)
        expired_count = 0
        
        for token in all_tokens:
            expires_at = token.expires_at
            # Handle both timezone-aware and timezone-naive datetimes
            if expires_at.tzinfo is None:
                # If timezone-naive, assume it's UTC
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            
            if expires_at < current_time:
                expired_count += 1
        
        return {
            "total_tokens": total_count,
            "expired_tokens": expired_count,
            "active_tokens": total_count - expired_count
        }
    except Exception as e:
        logger.error(f"Error getting token stats: {e}")
        return {
            "total_tokens": 0,
            "expired_tokens": 0,
            "active_tokens": 0
        }
