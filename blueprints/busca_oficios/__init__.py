"""
Blueprint para Busca Automática de Ofícios Requisitórios
"""

from flask import Blueprint, render_template, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
from service_busca_oficio import BuscaOficioService
import uuid
from datetime import datetime

busca_oficios_bp = Blueprint(
    'busca_oficios',
    __name__,
    url_prefix='/automacao/busca-oficios',
    template_folder='../../templates'
)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@busca_oficios_bp.route('/')
def index():
    """Página principal de busca de ofícios"""
    try:
        with open('templates/busca_oficios/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Módulo de Busca de Ofícios em construção", 404

@busca_oficios_bp.route('/api/upload-lista', methods=['POST'])
def upload_lista():
    """Upload de planilha com lista de precatórios"""
    try:
        if 'arquivo' not in request.files:
            return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['arquivo']
        
        if file.filename == '':
            return jsonify({'sucesso': False, 'erro': 'Arquivo sem nome'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Importar planilha
            resultado = BuscaOficioService.importar_planilha(filepath)
            
            if resultado.get('sucesso'):
                return jsonify({
                    'sucesso': True,
                    'total': resultado['total'],
                    'filepath': filepath
                }), 200
            else:
                return jsonify(resultado), 400
        
        return jsonify({'sucesso': False, 'erro': 'Tipo de arquivo não permitido'}), 400
        
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@busca_oficios_bp.route('/api/iniciar-busca', methods=['POST'])
def iniciar_busca():
    """Inicia busca automática"""
    try:
        dados = request.get_json()
        filepath = dados.get('filepath')
        certificado_path = dados.get('certificado_path')
        senha = dados.get('senha')
        
        # Importar lista
        resultado_import = BuscaOficioService.importar_planilha(filepath)
        
        if not resultado_import.get('sucesso'):
            return jsonify(resultado_import), 400
        
        precatorios = resultado_import['precatorios']
        
        # Criar serviço de busca
        service = BuscaOficioService(certificado_path, senha)
        
        # Processar lote
        lote_id = str(uuid.uuid4())
        
        def callback_progresso(atual, total, processo):
            print(f"Processando {atual}/{total}: {processo}")
        
        resultados = service.processar_lote(precatorios, callback_progresso)
        service.fechar_driver()
        
        # Estatísticas
        total = len(resultados)
        sucesso = len([r for r in resultados if r.get('sucesso')])
        
        return jsonify({
            'sucesso': True,
            'lote_id': lote_id,
            'total': total,
            'encontrados': sucesso,
            'resultados': resultados
        }), 200
        
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@busca_oficios_bp.route('/api/tribunais', methods=['GET'])
def listar_tribunais():
    """Lista tribunais disponíveis"""
    return jsonify({
        'sucesso': True,
        'tribunais': BuscaOficioService.TRIBUNAIS
    }), 200

@busca_oficios_bp.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'module': 'busca_oficios',
        'version': '1.0.0'
    }), 200
