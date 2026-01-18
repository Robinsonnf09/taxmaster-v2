// config/redis.js - Configuração Redis
const redis = require('redis');
const logger = require('./logger');

let redisClient;

async function connectRedis() {
  try {
    const redisUrl = process.env.REDIS_URL || 'redis://localhost:6379';
    
    redisClient = redis.createClient({
      url: redisUrl,
      socket: {
        reconnectStrategy: (retries) => {
          if (retries > 10) {
            logger.error('Redis: Máximo de tentativas excedido');
            return new Error('Redis connection failed');
          }
          return retries * 500;
        }
      }
    });

    redisClient.on('error', (err) => logger.error('Redis Error:', err));
    redisClient.on('connect', () => logger.info('✅ Redis conectado'));
    redisClient.on('reconnecting', () => logger.warn('⚠️ Redis reconectando...'));
    redisClient.on('ready', () => logger.info('🚀 Redis pronto!'));

    await redisClient.connect();
    return redisClient;
    
  } catch (error) {
    logger.error('❌ Erro ao conectar Redis:', error);
    logger.warn('⚠️ Usando MemoryStore como fallback');
    return null;
  }
}

module.exports = { connectRedis, getRedisClient: () => redisClient };
