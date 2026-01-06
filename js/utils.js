// Utilitários para o TAX MASTER
// Funções auxiliares usadas em todo o sistema

// Namespace global
var TAXMASTER = TAXMASTER || {};

// Módulo de utilitários
TAXMASTER.utils = {
    // Formatar valor monetário
    formatCurrency: function(value) {
        if (value === undefined || value === null) return 'N/A';
        
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    },
    
    // Formatar percentual
    formatPercent: function(value) {
        if (value === undefined || value === null) return 'N/A';
        
        return new Intl.NumberFormat('pt-BR', {
            style: 'percent',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    },
    
    // Formatar data
    formatDate: function(date) {
        if (!date) return 'N/A';
        
        if (typeof date === 'string') {
            date = new Date(date);
        }
        
        return new Intl.DateTimeFormat('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        }).format(date);
    },
    
    // Formatar data e hora
    formatDateTime: function(date) {
        if (!date) return 'N/A';
        
        if (typeof date === 'string') {
            date = new Date(date);
        }
        
        return new Intl.DateTimeFormat('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    },
    
    // Gerar ID único
    generateId: function() {
        return 'id_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    },
    
    // Validar CPF
    validateCPF: function(cpf) {
        cpf = cpf.replace(/[^\d]/g, '');
        
        if (cpf.length !== 11) return false;
        
        // Verificar se todos os dígitos são iguais
        if (/^(\d)\1+$/.test(cpf)) return false;
        
        // Validar dígitos verificadores
        let sum = 0;
        let remainder;
        
        for (let i = 1; i <= 9; i++) {
            sum += parseInt(cpf.substring(i - 1, i)) * (11 - i);
        }
        
        remainder = (sum * 10) % 11;
        
        if (remainder === 10 || remainder === 11) {
            remainder = 0;
        }
        
        if (remainder !== parseInt(cpf.substring(9, 10))) {
            return false;
        }
        
        sum = 0;
        
        for (let i = 1; i <= 10; i++) {
            sum += parseInt(cpf.substring(i - 1, i)) * (12 - i);
        }
        
        remainder = (sum * 10) % 11;
        
        if (remainder === 10 || remainder === 11) {
            remainder = 0;
        }
        
        if (remainder !== parseInt(cpf.substring(10, 11))) {
            return false;
        }
        
        return true;
    },
    
    // Validar CNPJ
    validateCNPJ: function(cnpj) {
        cnpj = cnpj.replace(/[^\d]/g, '');
        
        if (cnpj.length !== 14) return false;
        
        // Verificar se todos os dígitos são iguais
        if (/^(\d)\1+$/.test(cnpj)) return false;
        
        // Validar dígitos verificadores
        let size = cnpj.length - 2;
        let numbers = cnpj.substring(0, size);
        let digits = cnpj.substring(size);
        let sum = 0;
        let pos = size - 7;
        
        for (let i = size; i >= 1; i--) {
            sum += parseInt(numbers.charAt(size - i)) * pos--;
            if (pos < 2) pos = 9;
        }
        
        let result = sum % 11 < 2 ? 0 : 11 - (sum % 11);
        
        if (result !== parseInt(digits.charAt(0))) {
            return false;
        }
        
        size += 1;
        numbers = cnpj.substring(0, size);
        sum = 0;
        pos = size - 7;
        
        for (let i = size; i >= 1; i--) {
            sum += parseInt(numbers.charAt(size - i)) * pos--;
            if (pos < 2) pos = 9;
        }
        
        result = sum % 11 < 2 ? 0 : 11 - (sum % 11);
        
        if (result !== parseInt(digits.charAt(1))) {
            return false;
        }
        
        return true;
    },
    
    // Formatar CPF
    formatCPF: function(cpf) {
        cpf = cpf.replace(/[^\d]/g, '');
        
        return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    },
    
    // Formatar CNPJ
    formatCNPJ: function(cnpj) {
        cnpj = cnpj.replace(/[^\d]/g, '');
        
        return cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    },
    
    // Calcular valor presente
    calculatePresentValue: function(futureValue, rate, periods) {
        return futureValue / Math.pow(1 + rate, periods);
    },
    
    // Calcular valor futuro
    calculateFutureValue: function(presentValue, rate, periods) {
        return presentValue * Math.pow(1 + rate, periods);
    },
    
    // Calcular pagamento de amortização
    calculateAmortizationPayment: function(principal, rate, periods) {
        if (rate === 0) return principal / periods;
        
        const x = Math.pow(1 + rate, periods);
        return (principal * rate * x) / (x - 1);
    },
    
    // Gerar tabela de amortização
    generateAmortizationTable: function(principal, rate, periods) {
        const table = [];
        const payment = this.calculateAmortizationPayment(principal, rate, periods);
        let balance = principal;
        
        for (let i = 1; i <= periods; i++) {
            const interest = balance * rate;
            const amortization = payment - interest;
            balance -= amortization;
            
            if (i === periods) {
                // Ajustar última parcela para zerar saldo
                balance = 0;
            }
            
            table.push({
                numeroParcela: i,
                valorParcela: payment,
                juros: interest,
                amortizacao: amortization,
                saldoDevedor: balance
            });
        }
        
        return table;
    },
    
    // Calcular taxa interna de retorno (TIR)
    calculateIRR: function(cashflows) {
        const maxIterations = 1000;
        const tolerance = 0.0000001;
        
        let guess = 0.1;
        
        for (let i = 0; i < maxIterations; i++) {
            const npv = this.calculateNPV(cashflows, guess);
            const derivative = this.calculateNPVDerivative(cashflows, guess);
            
            if (Math.abs(npv) < tolerance) {
                return guess;
            }
            
            guess = guess - npv / derivative;
            
            if (guess <= -1) {
                guess = -0.999999;
            }
        }
        
        return null;
    },
    
    // Calcular valor presente líquido (VPL)
    calculateNPV: function(cashflows, rate) {
        let npv = cashflows[0];
        
        for (let i = 1; i < cashflows.length; i++) {
            npv += cashflows[i] / Math.pow(1 + rate, i);
        }
        
        return npv;
    },
    
    // Calcular derivada do VPL (para TIR)
    calculateNPVDerivative: function(cashflows, rate) {
        let derivative = 0;
        
        for (let i = 1; i < cashflows.length; i++) {
            derivative -= i * cashflows[i] / Math.pow(1 + rate, i + 1);
        }
        
        return derivative;
    },
    
    // Calcular taxa de juros efetiva
    calculateEffectiveRate: function(nominalRate, compoundingPeriodsPerYear) {
        return Math.pow(1 + nominalRate / compoundingPeriodsPerYear, compoundingPeriodsPerYear) - 1;
    },
    
    // Calcular ROI
    calculateROI: function(gain, cost) {
        return gain / cost;
    },
    
    // Converter taxa de juros (anual para mensal, etc.)
    convertInterestRate: function(rate, fromPeriod, toPeriod) {
        // fromPeriod e toPeriod podem ser: 'daily', 'monthly', 'quarterly', 'semiannual', 'annual'
        const periodsMap = {
            'daily': 365,
            'monthly': 12,
            'quarterly': 4,
            'semiannual': 2,
            'annual': 1
        };
        
        const fromPeriods = periodsMap[fromPeriod];
        const toPeriods = periodsMap[toPeriod];
        
        if (!fromPeriods || !toPeriods) {
            throw new Error('Período inválido');
        }
        
        // Converter para taxa efetiva anual
        const effectiveAnnualRate = Math.pow(1 + rate, fromPeriods) - 1;
        
        // Converter para taxa do período desejado
        return Math.pow(1 + effectiveAnnualRate, 1 / toPeriods) - 1;
    },
    
    // Formatar número com separador de milhares
    formatNumber: function(value, decimals = 2) {
        if (value === undefined || value === null) return 'N/A';
        
        return new Intl.NumberFormat('pt-BR', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(value);
    },
    
    // Validar email
    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    // Formatar número de telefone
    formatPhone: function(phone) {
        phone = phone.replace(/[^\d]/g, '');
        
        if (phone.length === 11) {
            return phone.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
        } else if (phone.length === 10) {
            return phone.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
        }
        
        return phone;
    },
    
    // Converter string para número
    parseNumber: function(value) {
        if (typeof value === 'number') return value;
        
        if (!value) return 0;
        
        // Remover formatação de moeda e percentual
        value = value.replace(/[^\d,.-]/g, '');
        
        // Converter vírgula para ponto
        value = value.replace(',', '.');
        
        return parseFloat(value);
    },
    
    // Calcular idade a partir da data de nascimento
    calculateAge: function(birthDate) {
        if (!birthDate) return null;
        
        if (typeof birthDate === 'string') {
            birthDate = new Date(birthDate);
        }
        
        const today = new Date();
        let age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        
        return age;
    },
    
    // Verificar se objeto está vazio
    isEmptyObject: function(obj) {
        return Object.keys(obj).length === 0;
    },
    
    // Clonar objeto
    cloneObject: function(obj) {
        return JSON.parse(JSON.stringify(obj));
    },
    
    // Arredondar número
    round: function(value, decimals = 2) {
        const factor = Math.pow(10, decimals);
        return Math.round(value * factor) / factor;
    },
    
    // Truncar número
    truncate: function(value, decimals = 2) {
        const factor = Math.pow(10, decimals);
        return Math.trunc(value * factor) / factor;
    },
    
    // Gerar número aleatório entre min e max
    random: function(min, max) {
        return Math.random() * (max - min) + min;
    },
    
    // Gerar número inteiro aleatório entre min e max
    randomInt: function(min, max) {
        min = Math.ceil(min);
        max = Math.floor(max);
        return Math.floor(Math.random() * (max - min + 1)) + min;
    },
    
    // Verificar se valor está entre min e max
    isBetween: function(value, min, max) {
        return value >= min && value <= max;
    },
    
    // Limitar valor entre min e max
    clamp: function(value, min, max) {
        return Math.min(Math.max(value, min), max);
    },
    
    // Interpolar linearmente entre a e b
    lerp: function(a, b, t) {
        return a + (b - a) * t;
    },
    
    // Mapear valor de um intervalo para outro
    map: function(value, fromMin, fromMax, toMin, toMax) {
        return toMin + (toMax - toMin) * ((value - fromMin) / (fromMax - fromMin));
    },
    
    // Verificar se string está vazia
    isEmptyString: function(str) {
        return !str || str.trim().length === 0;
    },
    
    // Capitalizar primeira letra
    capitalize: function(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1);
    },
    
    // Truncar string com ellipsis
    truncateString: function(str, maxLength) {
        if (!str) return '';
        if (str.length <= maxLength) return str;
        return str.slice(0, maxLength) + '...';
    },
    
    // Remover acentos
    removeAccents: function(str) {
        return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    },
    
    // Converter para slug
    slugify: function(str) {
        return this.removeAccents(str)
            .toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .replace(/[\s_-]+/g, '-')
            .replace(/^-+|-+$/g, '');
    },
    
    // Verificar se é dispositivo móvel
    isMobile: function() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    },
    
    // Obter parâmetros da URL
    getUrlParams: function() {
        const params = {};
        const queryString = window.location.search.substring(1);
        const pairs = queryString.split('&');
        
        for (let i = 0; i < pairs.length; i++) {
            const pair = pairs[i].split('=');
            params[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1] || '');
        }
        
        return params;
    },
    
    // Adicionar parâmetro à URL
    addUrlParam: function(url, param, value) {
        const separator = url.includes('?') ? '&' : '?';
        return `${url}${separator}${encodeURIComponent(param)}=${encodeURIComponent(value)}`;
    },
    
    // Copiar para área de transferência
    copyToClipboard: function(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        document.body.appendChild(textarea);
        textarea.select();
        
        try {
            document.execCommand('copy');
            return true;
        } catch (err) {
            console.error('Erro ao copiar para área de transferência:', err);
            return false;
        } finally {
            document.body.removeChild(textarea);
        }
    },
    
    // Debounce (limitar frequência de chamadas)
    debounce: function(func, wait) {
        let timeout;
        
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Throttle (garantir intervalo mínimo entre chamadas)
    throttle: function(func, limit) {
        let inThrottle;
        
        return function executedFunction(...args) {
            if (!inThrottle) {
                func(...args);
                inThrottle = true;
                setTimeout(() => {
                    inThrottle = false;
                }, limit);
            }
        };
    }
};

// Inicializar módulo de utilitários
console.log('Módulo de utilitários inicializado com sucesso');
