# Adicionar ao app.py após as rotas existentes

from flask import jsonify, request, send_file
from datetime import datetime
import json
from service_calculadora import CalculadoraService
from models_calculadora import CalculoPrecatorio
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

# Configurar banco para cálculos
engine_calculos = create_engine('sqlite:///calculos_precatorios.db')
SessionCalc = sessionmaker(bind=engine_calculos)

@app.route('/api/calculadora/calcular', methods=['POST'])
def api_calcular():
    """API para cálculo de precatórios"""
    try:
        dados = request.get_json()
        
        # Calcular
        resultado = CalculadoraService.calcular(dados)
        
        if not resultado.get('sucesso'):
            return jsonify(resultado), 400
        
        # Salvar no banco
        try:
            session = SessionCalc()
            calculo = CalculoPrecatorio(
                valor_original=float(dados['valor_original']),
                indice_correcao=dados['indice_correcao'],
                data_inicial=datetime.strptime(dados['data_inicial'], '%Y-%m-%d'),
                data_final=datetime.strptime(dados['data_final'], '%Y-%m-%d'),
                incluir_juros=dados.get('incluir_juros', False),
                taxa_juros=float(dados.get('taxa_juros', 0)),
                percentual_honorarios=float(dados.get('percentual_honorarios', 0)),
                valor_corrigido=resultado.get('valor_corrigido'),
                valor_juros=resultado.get('valor_juros'),
                valor_honorarios=resultado.get('valor_honorarios'),
                valor_liquido=resultado.get('valor_liquido'),
                detalhamento_json=json.dumps(resultado.get('detalhamento', [])),
                processo=dados.get('processo', ''),
                observacoes=dados.get('observacoes', '')
            )
            session.add(calculo)
            session.commit()
            resultado['id_calculo'] = calculo.id
            session.close()
        except Exception as e:
            print(f"Erro ao salvar cálculo: {e}")
        
        return jsonify(resultado), 200
        
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/calculadora/historico', methods=['GET'])
def api_historico():
    """Retorna histórico de cálculos"""
    try:
        limite = int(request.args.get('limite', 50))
        
        session = SessionCalc()
        calculos = session.query(CalculoPrecatorio)\
                         .order_by(CalculoPrecatorio.created_at.desc())\
                         .limit(limite)\
                         .all()
        
        resultado = [c.to_dict() for c in calculos]
        session.close()
        
        return jsonify({'sucesso': True, 'calculos': resultado}), 200
        
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/calculadora/comparar', methods=['POST'])
def api_comparar_indices():
    """Compara resultado entre múltiplos índices"""
    try:
        dados = request.get_json()
        indices = dados.get('indices', ['IPCA-E', 'SELIC', 'INPC'])
        
        resultado = CalculadoraService.comparar_indices(dados, indices)
        
        return jsonify(resultado), 200
        
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@app.route('/api/calculadora/indices', methods=['GET'])
def api_listar_indices():
    """Lista índices disponíveis"""
    return jsonify({
        'sucesso': True,
        'indices': CalculadoraService.INDICES_DISPONIVEIS
    }), 200

@app.route('/api/calculadora/validar', methods=['POST'])
def api_validar_dados():
    """Valida dados antes do cálculo"""
    try:
        dados = request.get_json()
        valido, erro = CalculadoraService.validar_dados(dados)
        
        return jsonify({
            'valido': valido,
            'erro': erro
        }), 200
        
    except Exception as e:
        return jsonify({'valido': False, 'erro': str(e)}), 400
