"""
Blueprint para busca automatizada de ofícios requisitórios
"""

from flask import Blueprint, render_template, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
from certificado_a3 import certificado_manager
from integracao_tribunais import TribunalIntegration
from processador_planilha import ProcessadorPlanilha
import threading

busca_oficios_bp = Blueprint(
    'busca_oficios',
    __name__,
    url_prefix='/automacao/busca-oficios',
    template_folder='../../templates'
)

# Configurações
UPLOAD_FOLDER = 'uploads/planilhas'
OFICIOS_FOLDER = 'oficios_baixados'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def extensao_permitida(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@busca_oficios_bp.route('/')
def index():
    """Página principal de busca de ofícios"""
    return render_template('busca_oficios.html')

@busca_oficios_bp.route('/api/upload-certificado', methods=['POST'])
def upload_certificado():
    """Upload e validação de certificado A3"""
    try:
        if 'certificado' not in request.files:
            return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado'}), 400
        
        arquivo = request.files['certificado']
        senha = request.form.get('senha', '')
        
        if arquivo.filename == '':
            return jsonify({'sucesso': False, 'erro': 'Arquivo vazio'}), 400
        
        # Salvar temporariamente
        filename = secure_filename(arquivo.filename)
        cert_path = os.path.join('certificados', filename)
        arquivo.save(cert_path)
        
        # Carregar certificado
        resultado = certificado_manager.carregar_certificado_pfx(cert_path, senha)
        
        if resultado['sucesso']:
            # Validar
            valido = certificado_manager.validar_certificado()
            resultado['valido'] = valido
            
            if not valido:
                resultado['aviso'] = 'Certificado expirado ou inválido'
        
        return jsonify(resultado), 200 if resultado['sucesso'] else 400
        
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@busca_oficios_bp.route('/api/upload-planilha', methods=['POST'])
def upload_planilha():
    """Upload de planilha com lista de processos"""
    try:
        if 'planilha' not in request.files:
            return jsonify({'sucesso': False, 'erro': 'Nenhum arquivo enviado'}), 400
        
        arquivo = request.files['planilha']
        
        if arquivo.filename == '':
            return jsonify({'sucesso': False, 'erro': 'Arquivo vazio'}), 400
        
        if not extensao_permitida(arquivo.filename):
            return jsonify({
                'sucesso': False,
                'erro': 'Formato não permitido. Use .xlsx, .xls ou .csv'
            }), 400
        
        # Salvar
        filename = secure_filename(arquivo.filename)
        planilha_path = os.path.join(UPLOAD_FOLDER, filename)
        arquivo.save(planilha_path)
        
        # Processar
        processador = ProcessadorPlanilha(planilha_path)
        resultado = processador.carregar_planilha()
        
        if resultado['sucesso']:
            # Validar colunas esperadas
            validacao = processador.validar_colunas(['numero_processo', 'tribunal'])
            resultado['validacao'] = validacao
            resultado['arquivo_salvo'] = planilha_path
        
        return jsonify(resultado), 200 if resultado['sucesso'] else 400
        
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@busca_oficios_bp.route('/api/iniciar-busca', methods=['POST'])
def iniciar_busca():
    """Inicia busca automatizada em lote"""
    try:
        dados = request.get_json()
        planilha_path = dados.get('planilha_path')
        
        if not planilha_path or not os.path.exists(planilha_path):
            return jsonify({'sucesso': False, 'erro': 'Planilha não encontrada'}), 400
        
        # Verificar certificado
        if not certificado_manager.validar_certificado():
            return jsonify({
                'sucesso': False,
                'erro': 'Certificado não carregado ou inválido'
            }), 400
        
        # Processar planilha
        processador = ProcessadorPlanilha(planilha_path)
        processador.carregar_planilha()
        processos = processador.obter_processos()
        
        # Iniciar busca em thread separada
        def executar_busca():
            for processo in processos:
                try:
                    tribunal = TribunalIntegration(
                        processo['tribunal'],
                        certificado_manager
                    )
                    
                    resultado = tribunal.buscar_oficio_requisitorio(
                        processo['numero_processo']
                    )
                    
                    status = 'sucesso' if resultado['sucesso'] else 'erro'
                    mensagem = resultado.get('mensagem', resultado.get('erro', ''))
                    
                    processador.adicionar_resultado(
                        processo['linha'],
                        status,
                        mensagem
                    )
                    
                    tribunal.fechar()
                    
                except Exception as e:
                    processador.adicionar_resultado(
                        processo['linha'],
                        'erro',
                        str(e)
                    )
            
            # Gerar relatório
            relatorio_path = os.path.join(
                UPLOAD_FOLDER,
                f'relatorio_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            )
            processador.gerar_relatorio(relatorio_path)
        
        # Executar em background
        thread = threading.Thread(target=executar_busca)
        thread.start()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Busca iniciada em background',
            'total_processos': len(processos)
        }), 200
        
    except Exception as e:
        return jsonify({'sucesso': False, 'erro': str(e)}), 500

@busca_oficios_bp.route('/api/status', methods=['GET'])
def status_busca():
    """Retorna status da busca em andamento"""
    # Implementar controle de status
    return jsonify({
        'em_andamento': False,
        'processados': 0,
        'total': 0
    }), 200
