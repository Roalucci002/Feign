const Logger = require('./logger');

class EmotionManager {
  constructor() {
    this.logger = new Logger();
    this.currentEmotion = 'neutral';
    this.emotionIntensity = 0.5;
    this.emotionHistory = [];
  }

  updateEmotion(userMessage, aiResponse) {
    // Simple emotion detection based on keywords
    const happiness = this.detectEmotionKeyword(userMessage + aiResponse, ['good', 'great', 'happy', 'love', 'thanks', 'ありがとう', '素晴らしい']);
    const sadness = this.detectEmotionKeyword(userMessage + aiResponse, ['sad', 'bad', 'sorry', 'sorry', '悲しい', 'つらい']);
    const surprise = this.detectEmotionKeyword(userMessage + aiResponse, ['what', 'wow', 'really', 'えっ', 'マジ']);
    const thinking = this.detectEmotionKeyword(userMessage + aiResponse, ['think', 'maybe', 'perhaps', 'うーん', 'うん']);

    if (happiness > 0.7) {
      this.currentEmotion = 'happy';
      this.emotionIntensity = happiness;
    } else if (sadness > 0.7) {
      this.currentEmotion = 'sad';
      this.emotionIntensity = sadness;
    } else if (surprise > 0.6) {
      this.currentEmotion = 'surprised';
      this.emotionIntensity = surprise;
    } else if (thinking > 0.5) {
      this.currentEmotion = 'thinking';
      this.emotionIntensity = thinking;
    } else {
      this.currentEmotion = 'neutral';
      this.emotionIntensity = 0.5;
    }

    this.emotionHistory.push({
      emotion: this.currentEmotion,
      intensity: this.emotionIntensity,
      timestamp: new Date()
    });

    // Keep only last 50 emotions
    if (this.emotionHistory.length > 50) {
      this.emotionHistory.shift();
    }
  }

  detectEmotionKeyword(text, keywords) {
    const lowerText = text.toLowerCase();
    const matchCount = keywords.filter(kw => lowerText.includes(kw.toLowerCase())).length;
    return Math.min(matchCount / keywords.length, 1.0);
  }

  getCurrentEmotion() {
    return this.currentEmotion;
  }

  getEmotionIntensity() {
    return this.emotionIntensity;
  }
}

module.exports = EmotionManager;
