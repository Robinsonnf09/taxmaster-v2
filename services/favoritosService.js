// services/favoritosService.js - Favoritos e Anotações
const logger = require('../config/logger');

class FavoritosService {
  constructor() {
    this.favoritos = new Map(); // usuarioId -> Set de números de processo
    this.anotacoes = new Map(); // usuarioId -> Map(numeroProcesso -> anotação)
  }

  adicionarFavorito(usuarioId, numeroProcesso) {
    if (!this.favoritos.has(usuarioId)) {
      this.favoritos.set(usuarioId, new Set());
    }
    
    this.favoritos.get(usuarioId).add(numeroProcesso);
    logger.info(`⭐ Favorito adicionado: ${numeroProcesso} por ${usuarioId}`);
    return true;
  }

  removerFavorito(usuarioId, numeroProcesso) {
    if (!this.favoritos.has(usuarioId)) return false;
    
    const removed = this.favoritos.get(usuarioId).delete(numeroProcesso);
    if (removed) {
      logger.info(`🗑️ Favorito removido: ${numeroProcesso} por ${usuarioId}`);
    }
    return removed;
  }

  listarFavoritos(usuarioId) {
    return Array.from(this.favoritos.get(usuarioId) || []);
  }

  isFavorito(usuarioId, numeroProcesso) {
    return this.favoritos.get(usuarioId)?.has(numeroProcesso) || false;
  }

  adicionarAnotacao(usuarioId, numeroProcesso, texto) {
    if (!this.anotacoes.has(usuarioId)) {
      this.anotacoes.set(usuarioId, new Map());
    }
    
    this.anotacoes.get(usuarioId).set(numeroProcesso, {
      texto,
      criadaEm: new Date(),
      atualizadaEm: new Date()
    });

    logger.info(`📝 Anotação criada: ${numeroProcesso} por ${usuarioId}`);
    return true;
  }

  obterAnotacao(usuarioId, numeroProcesso) {
    return this.anotacoes.get(usuarioId)?.get(numeroProcesso) || null;
  }

  listarAnotacoes(usuarioId) {
    const userAnotacoes = this.anotacoes.get(usuarioId);
    if (!userAnotacoes) return [];
    
    return Array.from(userAnotacoes.entries()).map(([numero, anotacao]) => ({
      numeroProcesso: numero,
      ...anotacao
    }));
  }

  removerAnotacao(usuarioId, numeroProcesso) {
    if (!this.anotacoes.has(usuarioId)) return false;
    
    const removed = this.anotacoes.get(usuarioId).delete(numeroProcesso);
    if (removed) {
      logger.info(`🗑️ Anotação removida: ${numeroProcesso} por ${usuarioId}`);
    }
    return removed;
  }
}

module.exports = new FavoritosService();
