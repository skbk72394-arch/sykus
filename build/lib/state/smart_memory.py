"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   Sykus Smart State & Memory                                                 ║
║                                                                              ║
║   Native database handling - no SQL required                                 ║
║   save user_data to local  →  Auto-generates SQLite                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sqlite3
import json
import pickle
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class SmartDBConfig:
    """Configuration for Smart Database"""
    db_path: str = "~/.sykus/data/sykus.db"
    auto_migrate: bool = True
    json_serialization: bool = True


class SmartMemory:
    """
    Smart Memory - Zero-configuration database
    
    Usage:
        save user_data to local      → Saves to SQLite
        load users from local        → Loads from SQLite
        save config to memory        → In-memory storage
    """
    
    def __init__(self, config: Optional[SmartDBConfig] = None):
        self.config = config or SmartDBConfig()
        self.db_path = Path(self.config.db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache
        self._memory: Dict[str, Any] = {}
        
        # Connection pool
        self._connections: Dict[str, sqlite3.Connection] = {}
    
    def _get_connection(self, db_name: str = 'default') -> sqlite3.Connection:
        """Get or create database connection"""
        if db_name not in self._connections:
            db_file = self.db_path if db_name == 'default' else self.db_path.parent / f'{db_name}.db'
            conn = sqlite3.connect(str(db_file), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self._connections[db_name] = conn
        return self._connections[db_name]
    
    def _ensure_table(self, table_name: str, db_name: str = 'default'):
        """Ensure a table exists"""
        conn = self._get_connection(db_name)
        cursor = conn.cursor()
        
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                data TEXT,
                type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
    
    def save(self, key: str, value: Any, to: str = 'local') -> bool:
        """
        Save data to storage
        
        Args:
            key: Identifier for the data
            value: Data to save
            to: Storage target ('local', 'memory', or custom db name)
        
        Returns:
            True if successful
        """
        try:
            if to == 'memory':
                # In-memory only
                self._memory[key] = value
                return True
            
            # Database storage
            table_name = self._key_to_table(key)
            self._ensure_table(table_name, to)
            
            conn = self._get_connection(to)
            cursor = conn.cursor()
            
            # Serialize value
            data_str, type_name = self._serialize(value)
            
            cursor.execute(f'''
                INSERT OR REPLACE INTO {table_name} (key, data, type, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (key, data_str, type_name))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"[SmartMemory] Save error: {e}")
            return False
    
    def load(self, key: str, from_: str = 'local', default: Any = None) -> Any:
        """
        Load data from storage
        
        Args:
            key: Identifier for the data
            from_: Storage source ('local', 'memory', or custom db name)
            default: Default value if not found
        
        Returns:
            The stored data or default
        """
        try:
            if from_ == 'memory':
                return self._memory.get(key, default)
            
            # Database storage
            table_name = self._key_to_table(key)
            
            conn = self._get_connection(from_)
            cursor = conn.cursor()
            
            cursor.execute(f'''
                SELECT data, type FROM {table_name}
                WHERE key = ?
                ORDER BY id DESC LIMIT 1
            ''', (key,))
            
            row = cursor.fetchone()
            if row:
                return self._deserialize(row['data'], row['type'])
            
            return default
            
        except Exception as e:
            print(f"[SmartMemory] Load error: {e}")
            return default
    
    def load_all(self, key_pattern: str, from_: str = 'local') -> List[Any]:
        """Load all matching entries"""
        try:
            table_name = self._key_to_table(key_pattern)
            
            conn = self._get_connection(from_)
            cursor = conn.cursor()
            
            cursor.execute(f'''
                SELECT data, type FROM {table_name}
                WHERE key LIKE ?
                ORDER BY created_at DESC
            ''', (f'%{key_pattern}%',))
            
            results = []
            for row in cursor.fetchall():
                results.append(self._deserialize(row['data'], row['type']))
            
            return results
            
        except Exception as e:
            print(f"[SmartMemory] Load all error: {e}")
            return []
    
    def search(self, table: str, where: Dict[str, Any], from_: str = 'local') -> List[Any]:
        """Search with conditions"""
        try:
            self._ensure_table(table, from_)
            
            conn = self._get_connection(from_)
            cursor = conn.cursor()
            
            # Build query
            conditions = []
            values = []
            for col, val in where.items():
                if col == 'contains':
                    # Full-text search on data
                    conditions.append('data LIKE ?')
                    values.append(f'%{val}%')
                else:
                    conditions.append(f'data LIKE ?')
                    values.append(f'%"{col}":%{val}%')
            
            where_clause = ' AND '.join(conditions) if conditions else '1=1'
            
            cursor.execute(f'''
                SELECT data, type FROM {table}
                WHERE {where_clause}
                ORDER BY created_at DESC
            ''', values)
            
            results = []
            for row in cursor.fetchall():
                results.append(self._deserialize(row['data'], row['type']))
            
            return results
            
        except Exception as e:
            print(f"[SmartMemory] Search error: {e}")
            return []
    
    def delete(self, key: str, from_: str = 'local') -> bool:
        """Delete data"""
        try:
            if from_ == 'memory':
                if key in self._memory:
                    del self._memory[key]
                return True
            
            table_name = self._key_to_table(key)
            
            conn = self._get_connection(from_)
            cursor = conn.cursor()
            
            cursor.execute(f'DELETE FROM {table_name} WHERE key = ?', (key,))
            conn.commit()
            
            return True
            
        except Exception as e:
            print(f"[SmartMemory] Delete error: {e}")
            return False
    
    def _key_to_table(self, key: str) -> str:
        """Convert key to table name"""
        # Use key as table name, or default to 'data'
        if '_' in key:
            return key.split('_')[0] + 's'
        return 'data'
    
    def _serialize(self, value: Any) -> tuple:
        """Serialize value to string"""
        if isinstance(value, str):
            return value, 'str'
        elif isinstance(value, (int, float)):
            return str(value), 'number'
        elif isinstance(value, bool):
            return str(value), 'bool'
        elif isinstance(value, (list, dict)):
            return json.dumps(value), 'json'
        else:
            # Try pickle for complex objects
            try:
                return pickle.dumps(value).hex(), 'pickle'
            except:
                return str(value), 'str'
    
    def _deserialize(self, data: str, type_name: str) -> Any:
        """Deserialize value from string"""
        if type_name == 'str':
            return data
        elif type_name == 'number':
            try:
                if '.' in data:
                    return float(data)
                return int(data)
            except:
                return data
        elif type_name == 'bool':
            return data.lower() == 'true'
        elif type_name == 'json':
            return json.loads(data)
        elif type_name == 'pickle':
            try:
                return pickle.loads(bytes.fromhex(data))
            except:
                return data
        return data
    
    def close(self):
        """Close all connections"""
        for conn in self._connections.values():
            conn.close()
        self._connections.clear()


# Global smart memory instance
_smart_memory = None

def get_smart_memory() -> SmartMemory:
    """Get global SmartMemory instance"""
    global _smart_memory
    if _smart_memory is None:
        _smart_memory = SmartMemory()
    return _smart_memory


# Convenience functions
def save(key: str, value: Any, to: str = 'local') -> bool:
    """Quick save function"""
    return get_smart_memory().save(key, value, to)


def load(key: str, from_: str = 'local', default: Any = None) -> Any:
    """Quick load function"""
    return get_smart_memory().load(key, from_, default)
