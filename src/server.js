const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const LLMManager = require('./llm_manager');
const MemoryManager = require('./memory_manager');
const SearchManager = require('./search_manager');
const TTSManager = require('./tts_manager');
const AvatarManager = require('./avatar_manager');
const EmotionManager = require('./emotion_manager');
const Logger = require('./logger');
const QRCodeGenerator = require('./qrcode_generator');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

const logger = new Logger();

// Middleware
app.use(express.json());
app.use(express.static('public'));

// Initialize managers
const llmManager = new LLMManager();
const memoryManager = new MemoryManager();
const searchManager = new SearchManager();
const ttsManager = new TTSManager();
const avatarManager = new AvatarManager();
const emotionManager = new EmotionManager();

let sessionId = null;
let isReiConnected = false;
let phoneConnected = false;

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/index.html'));
});

app.get('/api/qrcode', async (req, res) => {
  try {
    const qrCode = await QRCodeGenerator.generate(`http://localhost:${process.env.PORT}/connect`);
    res.json({ qrCode, connectionUrl: `http://localhost:${process.env.PORT}/connect` });
  } catch (err) {
    logger.error('QR Code generation failed', err);
    res.status(500).json({ error: 'QR Code generation failed' });
  }
});

app.get('/connect', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/phone.html'));
});

// WebSocket connection handling
wss.on('connection', (ws) => {
  logger.info('New WebSocket connection');

  ws.on('message', async (message) => {
    try {
      const data = JSON.parse(message);

      // Phone client
      if (data.type === 'phone_connect') {
        phoneConnected = true;
        sessionId = data.sessionId;
        logger.info(`Phone connected: ${sessionId}`);
        ws.send(JSON.stringify({ type: 'connected', message: 'Connected to Rei-chan' }));
        return;
      }

      // Chat message
      if (data.type === 'chat' && phoneConnected) {
        const userMessage = data.text;
        logger.info(`User message: ${userMessage}`);

        // Retrieve relevant memories
        const relevantMemories = await memoryManager.retrieveRelevant(userMessage);

        // Check if search is needed
        const needsSearch = searchManager.shouldSearch(userMessage, relevantMemories);

        let searchResults = null;
        if (needsSearch) {
          searchResults = await searchManager.search(userMessage);
          logger.info(`Search executed for: ${userMessage}`);
        }

        // Generate response using LLM
        const response = await llmManager.generateResponse({
          userMessage,
          relevantMemories,
          searchResults,
          emotionState: emotionManager.getCurrentEmotion()
        });

        // Update emotion based on interaction
        emotionManager.updateEmotion(userMessage, response);

        // Generate voice
        const voiceBuffer = await ttsManager.synthesize(response);

        // Save to memory
        await memoryManager.save({
          type: 'conversation',
          user_message: userMessage,
          ai_response: response,
          timestamp: new Date()
        });

        // Send response to phone
        ws.send(JSON.stringify({
          type: 'response',
          text: response,
          audio: voiceBuffer.toString('base64'),
          emotion: emotionManager.getCurrentEmotion()
        }));

        // Update avatar
        const avatarState = avatarManager.getStateForEmotion(emotionManager.getCurrentEmotion());
        wss.clients.forEach(client => {
          if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify({
              type: 'avatar_update',
              state: avatarState
            }));
          }
        });
      }
    } catch (err) {
      logger.error('WebSocket message handling error', err);
      ws.send(JSON.stringify({ type: 'error', message: 'An error occurred' }));
    }
  });

  ws.on('close', () => {
    logger.info('WebSocket connection closed');
    if (phoneConnected) phoneConnected = false;
  });
});

// Server startup
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  logger.info(`Rei-chan server running on http://localhost:${PORT}`);
  console.log(`\n\n===============================================`);
  console.log(`れいちゃん AI Companion System`);
  console.log(`Server: http://localhost:${PORT}`);
  console.log(`===============================================\n`);
  console.log(`Open http://localhost:${PORT} in your browser`);
  console.log(`Scan the QR code on your phone to connect\n`);
});

module.exports = app;
