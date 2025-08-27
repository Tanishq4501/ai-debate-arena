import sqlite3
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import os
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, db_path='debate_arena.db'):
        """Initialize SQLite database with thread safety"""
        self.db_path = db_path
        self.lock = threading.Lock()
        self._create_database()
        logger.info(f"Memory manager initialized with database: {db_path}")

    def _create_database(self):
        """Create database tables if they don't exist"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        topic TEXT NOT NULL,
                        agents TEXT NOT NULL,  -- JSON array
                        status TEXT DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ended_at TIMESTAMP,
                        metadata TEXT  -- JSON object
                    )
                """)
                
                # Debate statements table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS debate_statements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        agent TEXT NOT NULL,
                        type TEXT NOT NULL,
                        content TEXT NOT NULL,  -- JSON object
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT,  -- JSON object
                        FOREIGN KEY (session_id) REFERENCES sessions (id)
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_statements_session ON debate_statements(session_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_statements_timestamp ON debate_statements(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_statements_agent ON debate_statements(agent)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_statements_type ON debate_statements(type)")
                
                conn.commit()
                logger.info("Database tables created successfully")
                
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            raise

    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path, timeout=30.0)
                conn.row_factory = sqlite3.Row  # Enable dict-like access
                yield conn
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error in database connection: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def create_debate_session(self, topic: str, agent_names: List[str]) -> str:
        """Create a new debate session with validation"""
        try:
            if not topic or not topic.strip():
                raise ValueError("Topic cannot be empty")
            if not agent_names or len(agent_names) < 2:
                raise ValueError("At least 2 agents required")
            
            session_id = str(uuid.uuid4())
            agents_json = json.dumps(agent_names)
            metadata = json.dumps({
                "agent_count": len(agent_names),
                "estimated_duration": "30-45 minutes",
                "version": "2.1"
            })
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sessions (id, topic, agents, status, metadata)
                    VALUES (?, ?, ?, 'active', ?)
                """, (session_id, topic.strip(), agents_json, metadata))
                conn.commit()
            
            logger.info(f"Created debate session: {session_id} for topic: {topic}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating debate session: {e}")
            raise

    def save_to_memory(self, session_id: str, agent_name: str, statement_type: str, content: Any) -> bool:
        """Save debate statement with enhanced error handling and validation"""
        try:
            if not all([session_id, agent_name, statement_type]):
                logger.warning("Invalid parameters for save_to_memory")
                return False
            
            # Ensure content is serializable
            if isinstance(content, (dict, list)):
                content_json = json.dumps(content)
            else:
                content_json = json.dumps({"content": str(content)})
            
            metadata = json.dumps({
                "content_length": len(str(content)),
                "version": "2.1",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO debate_statements (session_id, agent, type, content, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (session_id, agent_name, statement_type, content_json, metadata))
                conn.commit()
            
            logger.debug(f"Saved {statement_type} for {agent_name} in session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving to memory: {e}")
            return False

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve session metadata with error handling"""
        try:
            if not session_id:
                return None
                
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
                row = cursor.fetchone()
                
                if row:
                    session = dict(row)
                    # Parse JSON fields
                    session['agents'] = json.loads(session['agents'])
                    if session['metadata']:
                        session['metadata'] = json.loads(session['metadata'])
                    logger.debug(f"Retrieved session: {session_id}")
                    return session
                else:
                    logger.warning(f"Session not found: {session_id}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving session {session_id}: {e}")
            return None

    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Retrieve full debate history for a session with optional limiting"""
        try:
            if not session_id:
                return []
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM debate_statements WHERE session_id = ? ORDER BY timestamp ASC"
                params = [session_id]
                
                if limit:
                    query += " LIMIT ?"
                    params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                history = []
                for row in rows:
                    statement = dict(row)
                    # Parse JSON content
                    statement['content'] = json.loads(statement['content'])
                    if statement['metadata']:
                        statement['metadata'] = json.loads(statement['metadata'])
                    history.append(statement)
                
                logger.debug(f"Retrieved {len(history)} statements for session {session_id}")
                return history
                
        except Exception as e:
            logger.error(f"Error retrieving session history for {session_id}: {e}")
            return []

    def get_agent_scores(self, session_id: str) -> List[Dict]:
        """Retrieve all scores for a session with enhanced filtering"""
        try:
            if not session_id:
                return []
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM debate_statements 
                    WHERE session_id = ? AND type = 'score' 
                    ORDER BY timestamp DESC
                """, (session_id,))
                rows = cursor.fetchall()
                
                scores = []
                for row in rows:
                    score = dict(row)
                    score['content'] = json.loads(score['content'])
                    if score['metadata']:
                        score['metadata'] = json.loads(score['metadata'])
                    scores.append(score)
                
                logger.debug(f"Retrieved {len(scores)} scores for session {session_id}")
                return scores
                
        except Exception as e:
            logger.error(f"Error retrieving scores for session {session_id}: {e}")
            return []

    def end_session(self, session_id: str) -> bool:
        """Mark a session as completed with additional metadata"""
        try:
            if not session_id:
                return False
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE sessions 
                    SET status = 'completed', ended_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (session_id,))
                success = cursor.rowcount > 0
                conn.commit()
            
            if success:
                logger.info(f"Session {session_id} marked as completed")
            else:
                logger.warning(f"Failed to end session {session_id} - session not found")
                
            return success
            
        except Exception as e:
            logger.error(f"Error ending session {session_id}: {e}")
            return False

    def get_recent_sessions(self, limit: int = 10, status: Optional[str] = None) -> List[Dict]:
        """Get recent debate sessions with optional status filtering"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                if status:
                    cursor.execute("""
                        SELECT * FROM sessions WHERE status = ? 
                        ORDER BY created_at DESC LIMIT ?
                    """, (status, limit))
                else:
                    cursor.execute("""
                        SELECT * FROM sessions 
                        ORDER BY created_at DESC LIMIT ?
                    """, (limit,))
                
                rows = cursor.fetchall()
                sessions = []
                
                for row in rows:
                    session = dict(row)
                    session['agents'] = json.loads(session['agents'])
                    if session['metadata']:
                        session['metadata'] = json.loads(session['metadata'])
                    sessions.append(session)
                
                logger.debug(f"Retrieved {len(sessions)} recent sessions")
                return sessions
                
        except Exception as e:
            logger.error(f"Error retrieving recent sessions: {e}")
            return []

    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Clean up old completed sessions and their statements"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Find old sessions
                cursor.execute("""
                    SELECT id FROM sessions 
                    WHERE status = 'completed' AND ended_at < ?
                """, (cutoff_date,))
                old_session_ids = [row[0] for row in cursor.fetchall()]
                
                if not old_session_ids:
                    return 0
                
                # Delete statements first
                placeholders = ','.join('?' * len(old_session_ids))
                cursor.execute(f"""
                    DELETE FROM debate_statements 
                    WHERE session_id IN ({placeholders})
                """, old_session_ids)
                statements_deleted = cursor.rowcount
                
                # Delete sessions
                cursor.execute(f"""
                    DELETE FROM sessions 
                    WHERE id IN ({placeholders})
                """, old_session_ids)
                sessions_deleted = cursor.rowcount
                
                conn.commit()
                
                logger.info(f"Cleaned up {sessions_deleted} old sessions and {statements_deleted} statements")
                return sessions_deleted
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0

    def get_session_statistics(self, session_id: str) -> Dict:
        """Get comprehensive statistics for a debate session"""
        try:
            if not session_id:
                return {}
            
            session = self.get_session(session_id)
            if not session:
                return {}
            
            history = self.get_session_history(session_id)
            
            # Calculate statistics
            stats = {
                "session_id": session_id,
                "topic": session.get("topic", "Unknown"),
                "status": session.get("status", "Unknown"),
                "created_at": session.get("created_at"),
                "ended_at": session.get("ended_at"),
                "total_statements": len(history),
                "agents": session.get("agents", []),
                "agent_count": len(session.get("agents", [])),
                "statement_types": {},
                "agent_participation": {}
            }
            
            # Analyze statements
            for statement in history:
                stmt_type = statement.get("type", "unknown")
                agent = statement.get("agent", "unknown")
                
                # Count by type
                stats["statement_types"][stmt_type] = stats["statement_types"].get(stmt_type, 0) + 1
                
                # Count by agent
                stats["agent_participation"][agent] = stats["agent_participation"].get(agent, 0) + 1
            
            # Calculate duration if session is completed
            if stats["ended_at"] and stats["created_at"]:
                # Parse datetime strings if they're strings
                if isinstance(stats["ended_at"], str):
                    ended_at = datetime.fromisoformat(stats["ended_at"].replace('Z', '+00:00'))
                else:
                    ended_at = stats["ended_at"]
                    
                if isinstance(stats["created_at"], str):
                    created_at = datetime.fromisoformat(stats["created_at"].replace('Z', '+00:00'))
                else:
                    created_at = stats["created_at"]
                
                duration = ended_at - created_at
                stats["duration_minutes"] = round(duration.total_seconds() / 60, 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating session statistics: {e}")
            return {}

    def health_check(self) -> Dict:
        """Check the health of the memory system"""
        try:
            health = {
                "status": "healthy",
                "database_connected": True,
                "timestamp": datetime.utcnow().isoformat(),
                "using_fallback": False
            }
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get collection stats
                cursor.execute("SELECT COUNT(*) FROM sessions")
                session_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM debate_statements")
                statement_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM sessions WHERE status = 'active'")
                active_sessions = cursor.fetchone()[0]
                
                health.update({
                    "total_sessions": session_count,
                    "total_statements": statement_count,
                    "active_sessions": active_sessions,
                    "database_size": os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                })
            
            return health
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "database_connected": False,
                "using_fallback": False
            }


# Initialize global memory manager
try:
    memory_manager = MemoryManager()
except Exception as e:
    logger.error(f"Failed to initialize memory manager: {e}")
    raise

# Convenience functions for backward compatibility
def create_debate_session(topic: str, agent_names: List[str]) -> str:
    return memory_manager.create_debate_session(topic, agent_names)

def save_to_memory(session_id: str, agent_name: str, statement_type: str, content: Any) -> bool:
    return memory_manager.save_to_memory(session_id, agent_name, statement_type, content)

def get_session(session_id: str) -> Optional[Dict]:
    return memory_manager.get_session(session_id)

def get_session_history(session_id: str, limit: Optional[int] = None) -> List[Dict]:
    return memory_manager.get_session_history(session_id, limit)

def get_agent_scores(session_id: str) -> List[Dict]:
    return memory_manager.get_agent_scores(session_id)

def end_session(session_id: str) -> bool:
    return memory_manager.end_session(session_id)

def get_recent_sessions(limit: int = 10, status: Optional[str] = None) -> List[Dict]:
    return memory_manager.get_recent_sessions(limit, status)

def cleanup_old_sessions(days_old: int = 30) -> int:
    return memory_manager.cleanup_old_sessions(days_old)

def get_session_statistics(session_id: str) -> Dict:
    return memory_manager.get_session_statistics(session_id)

def health_check() -> Dict:
    return memory_manager.health_check()