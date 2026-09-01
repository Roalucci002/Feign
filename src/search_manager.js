const axios = require('axios');
const Logger = require('./logger');

class SearchManager {
  constructor() {
    this.logger = new Logger();
    this.searchUrl = process.env.SEARXNG_URL || 'http://localhost:8888';
    this.keywords = [
      'current', 'today', 'now', 'latest', 'patch', 'update',
      'season', 'event', 'version', 'release', '今', '現在',
      '最新', 'current version', 'this patch', 'today\'s'
    ];
  }

  shouldSearch(userMessage, relevantMemories) {
    // Check if message contains keywords indicating freshness need
    const hasKeyword = this.keywords.some(kw => 
      userMessage.toLowerCase().includes(kw)
    );
    
    // Confidence threshold: if we're not sure, search
    const isUncertain = !relevantMemories || relevantMemories.length === 0;
    
    return hasKeyword || isUncertain;
  }

  async search(query) {
    try {
      this.logger.info(`Searching for: ${query}`);
      
      const response = await axios.get(`${this.searchUrl}/search`, {
        params: {
          q: query,
          format: 'json',
          language: 'ja'
        },
        timeout: process.env.SEARCH_TIMEOUT || 10000
      });

      const results = response.data.results || [];
      
      // Process and verify results
      const verified = results.slice(0, 3).map(result => ({
        title: result.title,
        url: result.url,
        summary: result.content,
        source: this.rateSource(result.url),
        date: this.extractDate(result.content)
      }));

      this.logger.info(`Search completed: ${verified.length} results`);
      return verified;
    } catch (err) {
      this.logger.error('Search error', err);
      return [];
    }
  }

  rateSource(url) {
    if (url.includes('.jp/official') || url.includes('/docs/')) return 'OFFICIAL';
    if (url.includes('wiki')) return 'WIKI';
    if (url.includes('reddit.com')) return 'COMMUNITY';
    return 'OTHER';
  }

  extractDate(content) {
    // Simple date extraction
    const dateMatch = content.match(/\d{4}[-\/]\d{2}[-\/]\d{2}/);
    return dateMatch ? dateMatch[0] : null;
  }
}

module.exports = SearchManager;
