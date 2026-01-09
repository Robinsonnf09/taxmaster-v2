"""
Blueprint da Calculadora de Precatórios
Módulo isolado e reutilizável
"""

from flask import Blueprint, render_template, request, jsonify
from calculadora import calculadora

# Criar Blueprint
calculadora_bp = Blueprint(
    'calculadora',
    __name__,
    url_prefix='/automacao/calculadora',
    template_folder='../../templates'
)

@calculadora_bp.route('/')
def index():
    """Página principal da calculadora"""
    try:
        with open('calculadora.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Erro: calculadora.html não encontrado", 404
    except Exception as e:
        return f"Erro ao carregar calculadora: {str(e)}", 500

@calculadora_bp.route('/api/calcular', methods=['POST'])
def api_calcular():
    """API para cálculo"""
    try:
        dados = request.get_json()
        
        # Validações básicas
        if not dados:
            return jsonify({'sucesso': False, 'erro': 'Dados não fornecidos'}), 400
        
        required = ['valor_original', 'indice_correcao', 'data_inicial', 'data_final']
        missing = [f for f in required if f not in dados]
        
        if missing:
            return jsonify({
                'sucesso': False,
                'erro': f'Campos obrigatórios faltando: {", ".join(missing)}'
            }), 400
        
        # Calcular
        resultado = calculadora(dados)
        
        if not resultado or 'erro' in resultado:
            return jsonify({
                'sucesso': False,
                'erro': resultado.get('erro', 'Erro desconhecido')
            }), 400
        
        resultado['sucesso'] = True
        return jsonify(resultado), 200
        
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@calculadora_bp.route('/api/indices', methods=['GET'])
def api_indices():
    """Lista índices disponíveis"""
    indices = {
        'IPCA-E': 'Índice de Preços ao Consumidor Amplo Especial',
        'INPC': 'Índice Nacional de Preços ao Consumidor',
        'SELIC': 'Taxa Selic',
        'TR': 'Taxa Referencial',
        'IGPM': 'Índice Geral de Preços do Mercado'
    }
    return jsonify({'sucesso': True, 'indices': indices}), 200

@calculadora_bp.route('/health', methods=['GET'])
def health_check():
    """Health check do módulo"""
    return jsonify({
        'status': 'ok',
        'module': 'calculadora',
        'version': '1.0.0'
    }), 200
