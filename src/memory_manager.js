const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');
const Logger = require('./logger');

class MemoryManager {
  constructor() {
    this.logger = new Logger();
    this.dbPath = process.env.MEMORY_DB_PATH || './memory_db/rei.db';
    this.db = null;
    this.initializeDatabase();
  }

  initializeDatabase() {
    // Ensure directory exists
    const dir = path.dirname(this.dbPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    this.db = new sqlite3.Database(this.dbPath, (err) => {
      if (err) {
        this.logger.error('Database initialization failed', err);
      } else {
        this.logger.info('Memory database initialized');
        this.createTables();
      }
    });
  }

  createTables() {
    const queries = [
      `CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        content TEXT NOT NULL,
        metadata TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        importance INTEGER DEFAULT 1
      )`,
      `CREATE TABLE IF NOT EXISTS conversation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_message TEXT NOT NULL,
        ai_response TEXT NOT NULL,
        emotion TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )`,
      `CREATE TABLE IF NOT EXISTS relationship_state (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )`
    ];

    queries.forEach(query => {
      this.db.run(query, (err) => {
        if (err) this.logger.error('Table creation error', err);
      });
    });
  }

  async save(memoryData) {
    return new Promise((resolve, reject) => {
      const { type, content, metadata } = memoryData;
      
      if (type === 'conversation') {
        const { user_message, ai_response, emotion } = memoryData;
        this.db.run(
          `INSERT INTO conversation_history (user_message, ai_response, emotion) VALUES (?, ?, ?)`,
          [user_message, ai_response, emotion || 'neutral'],
          (err) => {
            if (err) {
              this.logger.error('Failed to save conversation', err);
              reject(err);
            } else {
              resolve();
            }
          }
        );
      } else {
        this.db.run(
          `INSERT INTO memories (type, content, metadata) VALUES (?, ?, ?)`,
          [type, content, JSON.stringify(metadata || {})],
          (err) => {
            if (err) {
              this.logger.error('Failed to save memory', err);
              reject(err);
            } else {
              resolve();
            }
          }
        );
      }
    });
  }

  async retrieveRelevant(query) {
    return new Promise((resolve, reject) => {
      // Simple keyword matching for now
      // In production, use semantic search or embeddings
      this.db.all(
        `SELECT content FROM memories WHERE type != 'conversation' ORDER BY created_at DESC LIMIT 5`,
        (err, rows) => {
          if (err) {
            this.logger.error('Memory retrieval error', err);
            resolve([]);
          } else {
            resolve(rows || []);
          }
        }
      );
    });
  }

  async delete(memoryId) {
    return new Promise((resolve, reject) => {
      this.db.run(
        `DELETE FROM memories WHERE id = ?`,
        [memoryId],
        (err) => {
          if (err) reject(err);
          else resolve();
        }
      );
    });
  }

  async clearOldConversations(daysOld = 30) {
    return new Promise((resolve, reject) => {
      this.db.run(
        `DELETE FROM conversation_history WHERE created_at < datetime('now', '-' || ? || ' days')`,
        [daysOld],
        (err) => {
          if (err) reject(err);
          else resolve();
        }
      );
    });
  }
}

module.exports = MemoryManager;
