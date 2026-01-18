// middleware/validator.js - Validação de Dados
const Joi = require('joi');
const logger = require('../config/logger');

const schemas = {
  login: Joi.object({
    usuario: Joi.string().min(3).max(50).required(),
    senha: Joi.string().min(6).required()
  }),

  buscaProcessos: Joi.object({
    valorMin: Joi.number().min(0).optional(),
    valorMax: Joi.number().min(0).optional(),
    natureza: Joi.string().valid('Todas', 'Alimentar', 'Tributária', 'Previdenciária', 'Comum').optional(),
    anoLoa: Joi.alternatives().try(Joi.string().valid('Todos'), Joi.number().integer().min(2000).max(2050)).optional(),
    status: Joi.string().valid('Todos', 'Pendente', 'Pago', 'Em Análise').optional(),
    quantidade: Joi.number().integer().min(1).max(100).optional()
  }),

  numeroProcesso: Joi.object({
    numero: Joi.string().pattern(/^\d{7}-?\d{2}\.?\d{4}\.?\d\.?\d{2}\.?\d{4}$/).required()
  })
};

function validate(schemaName) {
  return (req, res, next) => {
    const schema = schemas[schemaName];
    
    if (!schema) {
      logger.error(`Schema '${schemaName}' não encontrado`);
      return next();
    }

    const data = req.method === 'GET' ? req.query : req.body;
    const { error, value } = schema.validate(data, { abortEarly: false });

    if (error) {
      const errors = error.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message
      }));

      logger.warn(`Validação falhou: ${JSON.stringify(errors)}`);

      return res.status(400).json({
        success: false,
        message: 'Dados inválidos',
        errors
      });
    }

    req.validatedData = value;
    next();
  };
}

module.exports = { validate, schemas };
