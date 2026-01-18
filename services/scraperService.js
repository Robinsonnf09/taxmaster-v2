// services/scraperService.js - Web Scraping Avançado DEPRE/ESAJ
const axios = require('axios');
const cheerio = require('cheerio');
const { wrapper } = require('axios-cookiejar-support');
const { CookieJar } = require('tough-cookie');
const logger = require('../config/logger');

const jar = new CookieJar();
const client = wrapper(axios.create({ jar, timeout: 30000 }));

const DEPRE_BASE_URL = 'https://www.tjsp.jus.br/Depre';
const ESAJ_BASE_URL = 'https://esaj.tjsp.jus.br';

class ScraperService {
  constructor() {
    this.userAgents = [
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    ];
  }

  getRandomUserAgent() {
    return this.userAgents[Math.floor(Math.random() * this.userAgents.length)];
  }

  async scrapeDEPRE(filters = {}, quantidade = 30) {
    logger.info('🌐 Iniciando scraping Portal DEPRE...');
    
    const processos = [];
    
    try {
      const url = `${DEPRE_BASE_URL}/Pesquisas/PesquisaPublica`;
      
      const response = await client.get(url, {
        headers: {
          'User-Agent': this.getRandomUserAgent(),
          'Accept': 'text/html,application/xhtml+xml,application/xml',
          'Accept-Language': 'pt-BR,pt;q=0.9',
          'Connection': 'keep-alive'
        }
      });

      const $ = cheerio.load(response.data);
      
      // Extrair ViewState para POST
      const viewState = $('input[name="__VIEWSTATE"]').val();
      const eventValidation = $('input[name="__EVENTVALIDATION"]').val();
      
      logger.debug(`ViewState: ${viewState ? 'OK' : 'FAIL'}`);

      // Realizar busca
      const formData = new URLSearchParams({
        '__VIEWSTATE': viewState || '',
        '__EVENTVALIDATION': eventValidation || '',
        'ctl00$conteudoPagina$ddlNatureza': filters.natureza === 'Alimentar' ? 'A' : 
                                              filters.natureza === 'Comum' ? 'C' : '',
        'ctl00$conteudoPagina$txtAnoLOA': filters.anoLoa || '',
        'ctl00$conteudoPagina$btnPesquisar': 'Pesquisar'
      });

      const searchResponse = await client.post(url, formData, {
        headers: {
          'User-Agent': this.getRandomUserAgent(),
          'Content-Type': 'application/x-www-form-urlencoded',
          'Referer': url
        }
      });

      const $results = cheerio.load(searchResponse.data);
      const linhas = $results('table tbody tr');
      
      logger.info(`📊 DEPRE retornou ${linhas.length} linhas`);
      
      linhas.each((index, element) => {
        if (processos.length >= quantidade) return false;
        
        const cols = $results(element).find('td');
        
        if (cols.length >= 5) {
          const processo = {
            numero: $results(cols[0]).text().trim(),
            credor: $results(cols[1]).text().trim(),
            valor: this.parseValor($results(cols[2]).text().trim()),
            natureza: this.mapearNatureza($results(cols[3]).text().trim()),
            anoLOA: parseInt($results(cols[4]).text().trim()) || new Date().getFullYear() + 1,
            status: 'Pendente',
            classe: 'Precatório',
            tribunal: 'TJ-SP',
            comarca: 'São Paulo',
            fonte: '✅ Portal DEPRE TJ-SP (WEB SCRAPING)',
            dataColeta: new Date().toISOString()
          };
          
          if (this.validarNumeroProcesso(processo.numero)) {
            processos.push(processo);
            logger.debug(`✅ Processo ${index + 1}: ${processo.numero}`);
          }
        }
      });
      
      logger.info(`✅ DEPRE: ${processos.length} processos coletados`);
      return processos;
      
    } catch (error) {
      logger.error(`❌ Erro DEPRE: ${error.message}`);
      return [];
    }
  }

  async enriquecerComESAJ(processo) {
    logger.debug(`🔍 Enriquecendo ${processo.numero} com ESAJ...`);
    
    try {
      const numeroLimpo = processo.numero.replace(/\D/g, '');
      const url = `${ESAJ_BASE_URL}/cpopg/show.do`;
      
      const response = await client.get(url, {
        params: {
          'processo.codigo': numeroLimpo,
          'conversationId': ''
        },
        headers: { 'User-Agent': this.getRandomUserAgent() }
      });

      const $ = cheerio.load(response.data);
      
      // Extrair dados adicionais
      const valorCausa = this.parseValor($('#valorAcaoProcesso').text());
      const assunto = $('#assuntoProcesso').text().trim();
      const classe = $('#classeProcesso').text().trim();
      
      // Extrair credores
      const credores = [];
      $('#tableTodasPartes tr').each((i, el) => {
        const tipo = $(el).find('td:first').text().trim();
        const nome = $(el).find('td:nth-child(2)').text().trim();
        
        if (tipo.match(/autor|exequente|requerente/i) && nome) {
          credores.push(nome);
        }
      });

      return {
        ...processo,
        valor: valorCausa > processo.valor ? valorCausa : processo.valor,
        credor: credores[0] || processo.credor,
        assunto: assunto || processo.assunto,
        classe: classe || processo.classe,
        fonte: processo.fonte + ' + ESAJ',
        enriquecido: true
      };
      
    } catch (error) {
      logger.warn(`⚠️ Erro ao enriquecer ${processo.numero}: ${error.message}`);
      return processo;
    }
  }

  parseValor(str) {
    if (!str) return 0;
    const limpo = str.replace(/[^\d,]/g, '').replace(',', '.');
    return parseFloat(limpo) || 0;
  }

  mapearNatureza(nat) {
    const n = (nat || '').toLowerCase();
    if (n.includes('alimentar') || n.includes('aliment')) return 'Alimentar';
    if (n.includes('tributár') || n.includes('tribut')) return 'Tributária';
    if (n.includes('previdenciár') || n.includes('previd')) return 'Previdenciária';
    return 'Comum';
  }

  validarNumeroProcesso(numero) {
    if (!numero || numero.length < 15) return false;
    const limpo = numero.replace(/\D/g, '');
    return limpo.length >= 20;
  }

  async delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

module.exports = new ScraperService();
