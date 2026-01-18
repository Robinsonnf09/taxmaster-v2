// middleware/cache.js - Sistema de Cache Inteligente
const logger = require('../config/logger');

class CacheManager {
  constructor(redisClient) {
    this.redis = redisClient;
    this.memoryCache = new Map();
    this.ttl = parseInt(process.env.CACHE_TTL) || 3600;
  }

  async get(key) {
    try {
      if (this.redis && this.redis.isOpen) {
        const data = await this.redis.get(key);
        if (data) {
          logger.debug(`✅ Cache HIT (Redis): ${key}`);
          return JSON.parse(data);
        }
      } else {
        const data = this.memoryCache.get(key);
        if (data && data.expiry > Date.now()) {
          logger.debug(`✅ Cache HIT (Memory): ${key}`);
          return data.value;
        } else if (data) {
          this.memoryCache.delete(key);
        }
      }
      
      logger.debug(`❌ Cache MISS: ${key}`);
      return null;
      
    } catch (error) {
      logger.error(`Erro ao ler cache: ${error.message}`);
      return null;
    }
  }

  async set(key, value, customTtl = null) {
    const ttl = customTtl || this.ttl;
    
    try {
      if (this.redis && this.redis.isOpen) {
        await this.redis.setEx(key, ttl, JSON.stringify(value));
        logger.debug(`💾 Cache SET (Redis): ${key} - TTL: ${ttl}s`);
      } else {
        this.memoryCache.set(key, {
          value,
          expiry: Date.now() + (ttl * 1000)
        });
        logger.debug(`💾 Cache SET (Memory): ${key} - TTL: ${ttl}s`);
      }
      
      return true;
      
    } catch (error) {
      logger.error(`Erro ao salvar cache: ${error.message}`);
      return false;
    }
  }

  async delete(key) {
    try {
      if (this.redis && this.redis.isOpen) {
        await this.redis.del(key);
      }
      this.memoryCache.delete(key);
      logger.debug(`🗑️ Cache DELETE: ${key}`);
      return true;
    } catch (error) {
      logger.error(`Erro ao deletar cache: ${error.message}`);
      return false;
    }
  }

  async clear() {
    try {
      if (this.redis && this.redis.isOpen) {
        await this.redis.flushAll();
      }
      this.memoryCache.clear();
      logger.info('🧹 Cache limpo completamente');
      return true;
    } catch (error) {
      logger.error(`Erro ao limpar cache: ${error.message}`);
      return false;
    }
  }

  cacheMiddleware(keyGenerator, ttl = null) {
    return async (req, res, next) => {
      const key = typeof keyGenerator === 'function' 
        ? keyGenerator(req) 
        : `${req.method}:${req.originalUrl}`;

      const cached = await this.get(key);
      
      if (cached) {
        return res.json(cached);
      }

      const originalJson = res.json.bind(res);
      res.json = (data) => {
        this.set(key, data, ttl);
        return originalJson(data);
      };

      next();
    };
  }
}

module.exports = CacheManager;
