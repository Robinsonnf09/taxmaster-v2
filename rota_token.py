# Adicionar no blueprints/busca_oficios/__init__.py

@busca_oficios_bp.route('/api/detectar-token', methods=['POST'])
def detectar_token():
    """Detecta token A3 conectado"""
    try:
        from token_a3 import TokenA3Manager
        
        manager = TokenA3Manager()
        
        # Detectar middleware
        if not manager.detectar_middleware():
            return jsonify({
                'sucesso': False,
                'erro': 'Middleware do token não instalado'
            }), 400
        
        # Validar token conectado
        if not manager.validar_token_conectado():
            return jsonify({
                'sucesso': False,
                'erro': 'Token não está conectado na USB'
            }), 400
        
        return jsonify({
            'sucesso': True,
            'middleware': manager.middleware_path,
            'fabricante': 'Detectado automaticamente'
        }), 200
        
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500
