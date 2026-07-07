/**
 * AgriTech JSON-based Chatbot Module
 * Provides intelligent response matching with fuzzy search capabilities
 */

class JSONChatbot {
  constructor() {
    this.responses = [];
    this.fallbackResponses = [];
    this.isLoaded = false;
    this.stopWords = new Set([
      'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'how',
      'i', 'in', 'is', 'it', 'of', 'on', 'or', 'that', 'the', 'to', 'was',
      'what', 'when', 'where', 'which', 'who', 'why', 'with', 'can', 'you',
      'me', 'my', 'we', 'our', 'about', 'please', 'tell'
    ]);
    this.loadResponses();
  }

  /**
   * Load responses from JSON file
   */
  async loadResponses() {
    try {
      const response = await fetch('./chatbot-responses.json');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.responses = data.responses || [];
      this.fallbackResponses = data.fallback_responses || [
        "I’m currently running in offline mode. You can ask me about soil health, crops, irrigation, or fertilizers."
      ];

      this.isLoaded = true;
      console.log('Chatbot responses loaded successfully');

    } catch (error) {
      console.error('Failed to load chatbot responses:', error);

      // Friendly agriculture-focused fallback
      this.responses = [];
      this.fallbackResponses = [
        "I’m currently running in offline mode. Here’s some general advice: focus on soil health, proper irrigation, and timely crop care."
      ];

      this.isLoaded = false;
    }
  }

  /**
   * Normalize user text for matching
   */
  normalizeText(text) {
    return String(text || '')
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  /**
   * Tokenize text and remove low-signal words
   */
  tokenize(text) {
    const normalized = this.normalizeText(text);
    if (!normalized) return [];

    return normalized
      .split(' ')
      .filter((word) => word.length > 1 && !this.stopWords.has(word));
  }

  /**
   * Calculate similarity between two strings using Levenshtein distance
   */
  calculateSimilarity(str1, str2) {
    str1 = str1.toLowerCase().trim();
    str2 = str2.toLowerCase().trim();

    if (str1 === str2) return 1.0;

    const longer = str1.length > str2.length ? str1 : str2;
    const shorter = str1.length > str2.length ? str2 : str1;

    if (longer.length === 0) return 1.0;

    const distance = this.levenshteinDistance(longer, shorter);
    return (longer.length - distance) / longer.length;
  }

  /**
   * Token overlap score using Jaccard similarity
   */
  calculateTokenOverlap(str1, str2) {
    const tokens1 = new Set(this.tokenize(str1));
    const tokens2 = new Set(this.tokenize(str2));

    if (tokens1.size === 0 || tokens2.size === 0) return 0;

    let intersection = 0;
    for (const token of tokens1) {
      if (tokens2.has(token)) intersection++;
    }

    const union = tokens1.size + tokens2.size - intersection;
    return union === 0 ? 0 : intersection / union;
  }

  /**
   * Calculate Levenshtein distance
   */
  levenshteinDistance(str1, str2) {
    const matrix = Array(str2.length + 1)
      .fill(null)
      .map(() => Array(str1.length + 1).fill(null));

    for (let i = 0; i <= str1.length; i++) matrix[0][i] = i;
    for (let j = 0; j <= str2.length; j++) matrix[j][0] = j;

    for (let j = 1; j <= str2.length; j++) {
      for (let i = 1; i <= str1.length; i++) {
        const substitutionCost = str1[i - 1] === str2[j - 1] ? 0 : 1;
        matrix[j][i] = Math.min(
          matrix[j][i - 1] + 1,
          matrix[j - 1][i] + 1,
          matrix[j - 1][i - 1] + substitutionCost
        );
      }
    }

    return matrix[str2.length][str1.length];
  }

  /**
   * Check if input contains key phrases
   */
  containsKeyPhrases(input, query) {
    const inputWords = this.tokenize(input);
    const queryWords = this.tokenize(query);

    if (this.normalizeText(input).includes(this.normalizeText(query))) {
      return 1.0;
    }

    let matches = 0;
    for (const queryWord of queryWords) {
      if (queryWord.length > 2) {
        for (const inputWord of inputWords) {
          if (inputWord.includes(queryWord) || queryWord.includes(inputWord)) {
            matches++;
            break;
          }
        }
      }
    }

    return queryWords.length > 0 ? matches / queryWords.length : 0;
  }

  /**
   * Build scored match details for one query
   */
  scoreQuery(input, query) {
    const normalizedInput = this.normalizeText(input);
    const normalizedQuery = this.normalizeText(query);

    const exactMatch = normalizedInput === normalizedQuery ? 1.0 : 0;
    const containsMatch =
      normalizedInput.includes(normalizedQuery) || normalizedQuery.includes(normalizedInput)
        ? 0.9
        : 0;
    const levenshteinSimilarity = this.calculateSimilarity(normalizedInput, normalizedQuery);
    const keyPhraseMatch = this.containsKeyPhrases(normalizedInput, normalizedQuery);
    const tokenOverlap = this.calculateTokenOverlap(normalizedInput, normalizedQuery);

    return Math.max(
      exactMatch,
      containsMatch,
      levenshteinSimilarity * 0.55 + tokenOverlap * 0.45,
      keyPhraseMatch * 0.75,
      tokenOverlap * 0.8
    );
  }

  /**
   * Normalize query field to array
   */
  getQueryVariants(responseObj) {
    if (!responseObj || !responseObj.query) return [];
    return Array.isArray(responseObj.query) ? responseObj.query : [responseObj.query];
  }

  /**
   * Build useful fallback with suggestions
   */
  buildFallbackResponse(userInput, rankedMatches) {
    const base = this.getRandomFallback();
    const suggestions = rankedMatches
      .filter((item) => item.score >= 0.2)
      .slice(0, 3)
      .map((item) => item.query)
      .filter(Boolean);

    if (suggestions.length === 0) {
      return `${base}\n\nTry asking about: crop recommendation, irrigation, soil health, or plant diseases.`;
    }

    return `${base}\n\nYou can also ask: ${suggestions.join(' | ')}`;
  }

  /**
   * Find best matching response
   */
  findBestMatch(userInput) {
    if (!this.isLoaded || this.responses.length === 0) {
      return {
        response: this.getRandomFallback(),
        matched: false,
        confidence: 0,
        matchedQuery: null
      };
    }

    const input = this.normalizeText(userInput);
    let bestMatch = null;
    let bestScore = 0;
    const threshold = 0.42;
    const rankedMatches = [];

    for (const responseObj of this.responses) {
      const queries = this.getQueryVariants(responseObj);
      let itemBestScore = 0;
      let itemBestQuery = '';

      for (const query of queries) {
        const score = this.scoreQuery(input, query);
        if (score > itemBestScore) {
          itemBestScore = score;
          itemBestQuery = query;
        }
      }

      rankedMatches.push({ query: itemBestQuery, score: itemBestScore });

      if (itemBestScore > bestScore && itemBestScore >= threshold) {
        bestScore = itemBestScore;
        bestMatch = responseObj;
      }
    }

    rankedMatches.sort((a, b) => b.score - a.score);

    if (bestMatch) {
      return {
        response: bestMatch.response,
        matched: true,
        confidence: bestScore,
        matchedQuery: rankedMatches[0] ? rankedMatches[0].query : null
      };
    }

    return {
      response: this.buildFallbackResponse(input, rankedMatches),
      matched: false,
      confidence: rankedMatches[0] ? rankedMatches[0].score : 0,
      matchedQuery: rankedMatches[0] ? rankedMatches[0].query : null
    };
  }

  /**
   * Get random fallback response
   */
  getRandomFallback() {
    if (!Array.isArray(this.fallbackResponses) || this.fallbackResponses.length === 0) {
      return "I’m currently running in offline mode. Please ask about farming topics.";
    }
    const randomIndex = Math.floor(Math.random() * this.fallbackResponses.length);
    return this.fallbackResponses[randomIndex];
  }

  /**
   * Get response for user input
   */
  async getResponse(userInput) {
    if (!this.isLoaded) {
      await this.loadResponses();
    }
    const result = this.findBestMatch(userInput);
    return result.response;
  }

  /**
   * Get response with confidence details for advanced handling
   */
  async getResponseDetails(userInput) {
    if (!this.isLoaded) {
      await this.loadResponses();
    }
    return this.findBestMatch(userInput);
  }

  /**
   * Runtime response addition (non-persistent)
   */
  addResponse(query, response) {
    this.responses.push({ query: query.toLowerCase(), response });
  }

  /**
   * Check readiness
   */
  isReady() {
    return this.isLoaded;
  }

  /**
   * Reload responses
   */
  async reload() {
    await this.loadResponses();
  }
}

// Export globally
window.JSONChatbot = JSONChatbot;

// Node.js compatibility
if (typeof module !== 'undefined' && module.exports) {
  module.exports = JSONChatbot;
}
