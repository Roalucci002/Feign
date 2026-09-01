const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const Logger = require('./logger');

class TTSManager {
  constructor() {
    this.logger = new Logger();
    this.engine = process.env.TTS_ENGINE || 'piper';
    this.voiceModel = process.env.TTS_VOICE || 'ja_JP-kokoro-v1.0.onnx';
    this.speed = process.env.TTS_SPEED || 0.95;
  }

  async synthesize(text) {
    try {
      if (this.engine === 'piper') {
        return await this.synthesizeWithPiper(text);
      }
      return Buffer.alloc(0);
    } catch (err) {
      this.logger.error('TTS synthesis error', err);
      return Buffer.alloc(0);
    }
  }

  async synthesizeWithPiper(text) {
    return new Promise((resolve, reject) => {
      try {
        const piper = spawn('piper', [
          '--model', this.voiceModel,
          '--speed', this.speed.toString()
        ]);

        let audioBuffer = Buffer.alloc(0);

        piper.stdout.on('data', (data) => {
          audioBuffer = Buffer.concat([audioBuffer, data]);
        });

        piper.stderr.on('data', (data) => {
          this.logger.warn(`Piper stderr: ${data}`);
        });

        piper.on('close', (code) => {
          if (code === 0) {
            this.logger.info(`TTS synthesized: ${text.substring(0, 50)}...`);
            resolve(audioBuffer);
          } else {
            reject(new Error(`Piper exited with code ${code}`));
          }
        });

        piper.stdin.write(text);
        piper.stdin.end();
      } catch (err) {
        reject(err);
      }
    });
  }
}

module.exports = TTSManager;
