// services/queueService.js - Sistema de Filas com Bull
const Queue = require('bull');
const logger = require('../config/logger');

class QueueService {
  constructor() {
    this.queues = {};
    this.redisConfig = {
      redis: {
        host: process.env.REDIS_HOST || 'redis.railway.internal',
        port: process.env.REDIS_PORT || 6379,
        password: process.env.REDIS_PASSWORD
      }
    };
  }

  createQueue(name, options = {}) {
    if (!this.queues[name]) {
      this.queues[name] = new Queue(name, this.redisConfig);
      
      this.queues[name].on('completed', (job) => {
        logger.info(`✅ Job ${job.id} (${name}) completado`);
      });

      this.queues[name].on('failed', (job, err) => {
        logger.error(`❌ Job ${job.id} (${name}) falhou: ${err.message}`);
      });

      logger.info(`📋 Fila '${name}' criada`);
    }
    
    return this.queues[name];
  }

  async addJob(queueName, data, options = {}) {
    const queue = this.createQueue(queueName);
    
    const job = await queue.add(data, {
      attempts: 3,
      backoff: {
        type: 'exponential',
        delay: 2000
      },
      removeOnComplete: true,
      removeOnFail: false,
      ...options
    });

    logger.info(`📤 Job ${job.id} adicionado à fila '${queueName}'`);
    return job;
  }

  processQueue(queueName, processor) {
    const queue = this.createQueue(queueName);
    queue.process(processor);
    logger.info(`⚙️ Processador registrado para fila '${queueName}'`);
  }

  async getQueueStats(queueName) {
    const queue = this.queues[queueName];
    if (!queue) return null;

    const [waiting, active, completed, failed, delayed] = await Promise.all([
      queue.getWaitingCount(),
      queue.getActiveCount(),
      queue.getCompletedCount(),
      queue.getFailedCount(),
      queue.getDelayedCount()
    ]);

    return { waiting, active, completed, failed, delayed };
  }
}

module.exports = new QueueService();
