const fs = require('fs');
const path = require('path');

class Logger {
  constructor() {
    this.logDir = './logs';
    this.logFile = path.join(this.logDir, 'system.log');
    
    if (!fs.existsSync(this.logDir)) {
      fs.mkdirSync(this.logDir, { recursive: true });
    }
  }

  log(level, message, error = null) {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] [${level}] ${message}${error ? ` - ${error.message}` : ''}\n`;
    
    console.log(logEntry.trim());
    
    fs.appendFileSync(this.logFile, logEntry);
  }

  info(message) {
    this.log('INFO', message);
  }

  warn(message, error = null) {
    this.log('WARN', message, error);
  }

  error(message, error = null) {
    this.log('ERROR', message, error);
  }

  debug(message) {
    if (process.env.DEBUG === 'true') {
      this.log('DEBUG', message);
    }
  }
}

module.exports = Logger;
