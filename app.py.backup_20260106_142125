"""
Tax Master - Dashboard Web Completo
Sistema de Gestão de Precatórios com Automação Inteligente
Versão: 2.0
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_cors import CORS
import sys
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_

sys.path.append("src")
from database import SessionLocal
from models_atualizado import Processo, LogBuscaOficio, Contato, StatusProcessoEnum, TribunalEnum, NaturezaEnum

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'tax-master-2026-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Configurações
PROCESSOS_POR_PAGINA = 20

@app.route('/')
def index():
    """Página inicial - Dashboard"""
    db = SessionLocal()
    
    try:
        # Estatísticas gerais
        total_processos = db.query(Processo).count()
        total_valor = db.query(func.sum(Processo.valor_atualizado)).scalar() or 0
        processos_com_oficio = db.query(Processo).filter(Processo.tem_oficio == True).count()
        processos_pendentes = db.query(Processo).filter(Processo.status == StatusProcessoEnum.PENDENTE).count()
        
        # Estatísticas por tribunal
        por_tribunal = db.query(
            Processo.tribunal,
            func.count(Processo.id).label('total'),
            func.sum(Processo.valor_atualizado).label('valor_total')
        ).group_by(Processo.tribunal).all()
        
        # Estatísticas por natureza
        por_natureza = db.query(
            Processo.natureza,
            func.count(Processo.id).label('total'),
            func.sum(Processo.valor_atualizado).label('valor_total')
        ).group_by(Processo.natureza).all()
        
        # Processos recentes
        processos_recentes = db.query(Processo).order_by(
            Processo.data_cadastro.desc()
        ).limit(10).all()
        
        # Logs de busca recentes
        logs_recentes = db.query(LogBuscaOficio).order_by(
            LogBuscaOficio.data_busca.desc()
        ).limit(10).all()
        
        # Taxa de sucesso das buscas
        total_buscas = db.query(LogBuscaOficio).count()
        buscas_sucesso = db.query(LogBuscaOficio).filter(LogBuscaOficio.sucesso == True).count()
        taxa_sucesso = (buscas_sucesso / total_buscas * 100) if total_buscas > 0 else 0
        
        # Processos prioritários
        processos_prioritarios = db.query(Processo).filter(
            or_(
                Processo.credor_idoso == True,
                Processo.credor_doenca_grave == True,
                Processo.credor_deficiente == True
            )
        ).count()
        
        return render_template('dashboard.html',
            total_processos=total_processos,
            total_valor=total_valor,
            processos_com_oficio=processos_com_oficio,
            processos_pendentes=processos_pendentes,
            por_tribunal=por_tribunal,
            por_natureza=por_natureza,
            processos_recentes=processos_recentes,
            logs_recentes=logs_recentes,
            taxa_sucesso=taxa_sucesso,
            processos_prioritarios=processos_prioritarios
        )
        
    finally:
        db.close()

@app.route('/processos')
def listar_processos():
    """Lista de processos com filtros avançados"""
    db = SessionLocal()
    
    try:
        # Parâmetros de filtro
        tribunal = request.args.get('tribunal')
        esfera = request.args.get('esfera')
        natureza = request.args.get('natureza')
        status = request.args.get('status')
        ano_precatorio = request.args.get('ano_precatorio', type=int)
        valor_min = request.args.get('valor_min', type=float)
        valor_max = request.args.get('valor_max', type=float)
        tem_oficio = request.args.get('tem_oficio')
        prioritario = request.args.get('prioritario')
        situacao_pagamento = request.args.get('situacao_pagamento')  # NOVO
        busca = request.args.get('busca')
        pagina = request.args.get('pagina', 1, type=int)
        
        # Query base
        query = db.query(Processo)
        
        # Aplicar filtros
        if tribunal:
            query = query.filter(Processo.tribunal == TribunalEnum[tribunal])
        
        if esfera:
            from models_atualizado import EsferaEnum
            query = query.filter(Processo.esfera == EsferaEnum[esfera])
        
        if natureza:
            query = query.filter(Processo.natureza == NaturezaEnum[natureza])
        
        if status:
            query = query.filter(Processo.status == StatusProcessoEnum[status])
        
        if ano_precatorio:
            query = query.filter(Processo.ano_precatorio == ano_precatorio)
        
        if valor_min:
            query = query.filter(Processo.valor_atualizado >= valor_min)
        
        if valor_max:
            query = query.filter(Processo.valor_atualizado <= valor_max)
        
        if tem_oficio == 'sim':
            query = query.filter(Processo.tem_oficio == True)
        elif tem_oficio == 'nao':
            query = query.filter(Processo.tem_oficio == False)
        
        if prioritario == 'sim':
            query = query.filter(
                or_(
                    Processo.credor_idoso == True,
                    Processo.credor_doenca_grave == True,
                    Processo.credor_deficiente == True
                )
            )
        elif prioritario == 'nao':
            query = query.filter(
                and_(
                    Processo.credor_idoso == False,
                    Processo.credor_doenca_grave == False,
                    Processo.credor_deficiente == False
                )
            )
        
        # NOVO: Filtro de situação de pagamento com 3 opções
        if situacao_pagamento == 'com_pendencia':
            # Com pendência: possui_pendencia_pagamento = True
            query = query.filter(Processo.possui_pendencia_pagamento == True)
        elif situacao_pagamento == 'pronto_nao_pago':
            # Pronto e não pago: sem pendência MAS status != PAGO
            query = query.filter(
                and_(
                    Processo.possui_pendencia_pagamento == False,
                    Processo.status != StatusProcessoEnum.PAGO
                )
            )
        elif situacao_pagamento == 'pago':
            # Pago: status = PAGO
            query = query.filter(Processo.status == StatusProcessoEnum.PAGO)
        
        if busca:
            query = query.filter(
                or_(
                    Processo.numero_processo.contains(busca),
                    Processo.processo_principal.contains(busca),
                    Processo.credor_nome.contains(busca),
                    Processo.advogado_nome.contains(busca),
                    Processo.numero_oficio.contains(busca)
                )
            )
        
        # Ordenação
        ordenar_por = request.args.get('ordenar', 'data_cadastro')
        ordem = request.args.get('ordem', 'desc')
        
        if ordenar_por == 'valor':
            query = query.order_by(Processo.valor_atualizado.desc() if ordem == 'desc' else Processo.valor_atualizado.asc())
        elif ordenar_por == 'credor':
            query = query.order_by(Processo.credor_nome.asc() if ordem == 'asc' else Processo.credor_nome.desc())
        else:
            query = query.order_by(Processo.data_cadastro.desc() if ordem == 'desc' else Processo.data_cadastro.asc())
        
        # Calcular estatísticas dos resultados ANTES da paginação
        total = query.count()
        
        # Calcular valor total e estatísticas
        todos_processos = query.all()
        valor_total = sum(p.valor_atualizado for p in todos_processos) if todos_processos else 0
        
        # Contar com ofício
        com_oficio = sum(1 for p in todos_processos if p.tem_oficio)
        
        # Contar com pendência
        com_pendencia = sum(1 for p in todos_processos if p.possui_pendencia_pagamento)
        
        # Contar pronto e não pago (NOVO)
        pronto_nao_pago = sum(1 for p in todos_processos if not p.possui_pendencia_pagamento and p.status.name != 'PAGO')
        
        # Contar pagos (NOVO)
        pagos = sum(1 for p in todos_processos if p.status.name == 'PAGO')
        
        # Paginação
        processos = query.offset((pagina - 1) * PROCESSOS_POR_PAGINA).limit(PROCESSOS_POR_PAGINA).all()
        
        total_paginas = (total + PROCESSOS_POR_PAGINA - 1) // PROCESSOS_POR_PAGINA
        
        return render_template('processos.html',
            processos=processos,
            pagina=pagina,
            total_paginas=total_paginas,
            total=total,
            valor_total=valor_total,
            com_oficio=com_oficio,
            com_pendencia=com_pendencia,
            pronto_nao_pago=pronto_nao_pago,
            pagos=pagos,
            tribunais=TribunalEnum,
            naturezas=NaturezaEnum,
            status_list=StatusProcessoEnum
        )
        
    finally:
        db.close()

@app.route('/processo/cadastrar', methods=['GET', 'POST'])
def cadastrar_processo():
    """Cadastrar novo processo"""
    if request.method == 'GET':
        return render_template('processo_cadastrar.html')
    
    db = SessionLocal()
    
    try:
        # Coletar dados do formulário
        novo_processo = Processo(
            numero_processo=request.form.get('numero_processo'),
            processo_principal=request.form.get('processo_principal'),
            tribunal=TribunalEnum[request.form.get('tribunal')],
            natureza=NaturezaEnum[request.form.get('natureza')] if request.form.get('natureza') else None,
            status=StatusProcessoEnum[request.form.get('status', 'PENDENTE')],
            
            # Credor
            credor_nome=request.form.get('credor_nome'),
            credor_cpf_cnpj=request.form.get('credor_cpf_cnpj'),
            credor_email=request.form.get('credor_email'),
            credor_telefone=request.form.get('credor_telefone'),
            credor_endereco=request.form.get('credor_endereco'),
            credor_idoso=bool(request.form.get('credor_idoso')),
            credor_doenca_grave=bool(request.form.get('credor_doenca_grave')),
            credor_deficiente=bool(request.form.get('credor_deficiente')),
            
            # Advogado
            advogado_nome=request.form.get('advogado_nome'),
            advogado_oab=request.form.get('advogado_oab'),
            advogado_email=request.form.get('advogado_email'),
            advogado_telefone=request.form.get('advogado_telefone'),
            
            # Valores
            valor_principal=float(request.form.get('valor_principal')),
            valor_juros=float(request.form.get('valor_juros', 0)),
            valor_atualizado=float(request.form.get('valor_atualizado')),
            data_base_calculo=datetime.strptime(request.form.get('data_base_calculo'), '%Y-%m-%d').date() if request.form.get('data_base_calculo') else None,
            
            # Datas
            data_ajuizamento=datetime.strptime(request.form.get('data_ajuizamento'), '%Y-%m-%d').date() if request.form.get('data_ajuizamento') else None,
            data_transito_julgado=datetime.strptime(request.form.get('data_transito_julgado'), '%Y-%m-%d').date() if request.form.get('data_transito_julgado') else None,
            data_expedicao_oficio=datetime.strptime(request.form.get('data_expedicao_oficio'), '%Y-%m-%d').date() if request.form.get('data_expedicao_oficio') else None,
            
            # Informações adicionais
            classe=request.form.get('classe'),
            assunto=request.form.get('assunto'),
            area=request.form.get('area'),
            observacoes=request.form.get('observacoes'),
            tags=request.form.get('tags')
        )
        
        db.add(novo_processo)
        db.commit()
        
        return redirect(url_for('detalhe_processo', processo_id=novo_processo.id))
        
    except Exception as e:
        db.rollback()
        return f"Erro ao cadastrar processo: {str(e)}", 500
        
    finally:
        db.close()

@app.route('/processo/<int:processo_id>')
def detalhe_processo(processo_id):
    """Detalhes de um processo específico"""
    db = SessionLocal()
    
    try:
        processo = db.query(Processo).filter(Processo.id == processo_id).first()
        
        if not processo:
            return "Processo não encontrado", 404
        
        # Buscar logs de busca deste processo
        logs = db.query(LogBuscaOficio).filter(
            LogBuscaOficio.processo_id == processo_id
        ).order_by(LogBuscaOficio.data_busca.desc()).all()
        
        # Buscar contatos relacionados
        contatos = db.query(Contato).filter(
            Contato.processo_id == processo_id
        ).all()
        
        return render_template('processo_detalhe.html',
            processo=processo,
            logs=logs,
            contatos=contatos
        )
        
    finally:
        db.close()

@app.route('/processo/<int:processo_id>/editar', methods=['GET', 'POST'])
def editar_processo(processo_id):
    """Editar processo existente"""
    db = SessionLocal()
    
    try:
        processo = db.query(Processo).filter(Processo.id == processo_id).first()
        
        if not processo:
            return "Processo não encontrado", 404
        
        if request.method == 'GET':
            return render_template('processo_editar.html', processo=processo)
        
        # Atualizar dados
        processo.numero_processo = request.form.get('numero_processo')
        processo.processo_principal = request.form.get('processo_principal')
        processo.tribunal = TribunalEnum[request.form.get('tribunal')]
        processo.natureza = NaturezaEnum[request.form.get('natureza')] if request.form.get('natureza') else None
        processo.status = StatusProcessoEnum[request.form.get('status')]
        
        # Credor
        processo.credor_nome = request.form.get('credor_nome')
        processo.credor_cpf_cnpj = request.form.get('credor_cpf_cnpj')
        processo.credor_email = request.form.get('credor_email')
        processo.credor_telefone = request.form.get('credor_telefone')
        processo.credor_endereco = request.form.get('credor_endereco')
        processo.credor_idoso = bool(request.form.get('credor_idoso'))
        processo.credor_doenca_grave = bool(request.form.get('credor_doenca_grave'))
        processo.credor_deficiente = bool(request.form.get('credor_deficiente'))
        
        # Advogado
        processo.advogado_nome = request.form.get('advogado_nome')
        processo.advogado_oab = request.form.get('advogado_oab')
        processo.advogado_email = request.form.get('advogado_email')
        processo.advogado_telefone = request.form.get('advogado_telefone')
        
        # Valores
        processo.valor_principal = float(request.form.get('valor_principal'))
        processo.valor_juros = float(request.form.get('valor_juros', 0))
        processo.valor_atualizado = float(request.form.get('valor_atualizado'))
        processo.data_base_calculo = datetime.strptime(request.form.get('data_base_calculo'), '%Y-%m-%d').date() if request.form.get('data_base_calculo') else None
        
        # Datas
        processo.data_ajuizamento = datetime.strptime(request.form.get('data_ajuizamento'), '%Y-%m-%d').date() if request.form.get('data_ajuizamento') else None
        processo.data_transito_julgado = datetime.strptime(request.form.get('data_transito_julgado'), '%Y-%m-%d').date() if request.form.get('data_transito_julgado') else None
        processo.data_expedicao_oficio = datetime.strptime(request.form.get('data_expedicao_oficio'), '%Y-%m-%d').date() if request.form.get('data_expedicao_oficio') else None
        
        # Informações adicionais
        processo.classe = request.form.get('classe')
        processo.assunto = request.form.get('assunto')
        processo.area = request.form.get('area')
        processo.observacoes = request.form.get('observacoes')
        processo.tags = request.form.get('tags')
        
        db.commit()
        
        return redirect(url_for('detalhe_processo', processo_id=processo.id))
        
    except Exception as e:
        db.rollback()
        return f"Erro ao editar processo: {str(e)}", 500
        
    finally:
        db.close()

@app.route('/processo/<int:processo_id>/deletar', methods=['POST'])
def deletar_processo(processo_id):
    """Deletar processo"""
    db = SessionLocal()
    
    try:
        processo = db.query(Processo).filter(Processo.id == processo_id).first()
        
        if not processo:
            return jsonify({"sucesso": False, "erro": "Processo não encontrado"}), 404
        
        db.delete(processo)
        db.commit()
        
        return jsonify({"sucesso": True, "mensagem": "Processo deletado com sucesso"})
        
    except Exception as e:
        db.rollback()
        return jsonify({"sucesso": False, "erro": str(e)}), 500
        
    finally:
        db.close()

@app.route('/automacao')
def automacao():
    """Página de automação de buscas"""
    db = SessionLocal()
    
    try:
        # Estatísticas de automação
        total_logs = db.query(LogBuscaOficio).count()
        logs_sucesso = db.query(LogBuscaOficio).filter(LogBuscaOficio.sucesso == True).count()
        logs_falha = db.query(LogBuscaOficio).filter(LogBuscaOficio.sucesso == False).count()
        
        # Tempo médio de execução
        tempo_medio = db.query(func.avg(LogBuscaOficio.tempo_execucao)).scalar() or 0
        
        # Logs recentes
        logs_recentes = db.query(LogBuscaOficio).order_by(
            LogBuscaOficio.data_busca.desc()
        ).limit(50).all()
        
        # Processos sem ofício
        processos_sem_oficio = db.query(Processo).filter(
            Processo.tem_oficio == False
        ).count()
        
        return render_template('automacao.html',
            total_logs=total_logs,
            logs_sucesso=logs_sucesso,
            logs_falha=logs_falha,
            tempo_medio=tempo_medio,
            logs_recentes=logs_recentes,
            processos_sem_oficio=processos_sem_oficio,
            tribunais=TribunalEnum
        )
        
    finally:
        db.close()

@app.route('/api/iniciar-automacao', methods=['POST'])
def iniciar_automacao():
    """API para iniciar automação de buscas"""
    try:
        dados = request.json
        tribunal = dados.get('tribunal', 'TJSP')
        limite = dados.get('limite')
        
        # Aqui você integraria com o módulo de automação
        # Por enquanto, retorna sucesso simulado
        
        return jsonify({
            "sucesso": True,
            "mensagem": f"Automação iniciada para {tribunal}",
            "processos_agendados": limite or "todos"
        })
        
    except Exception as e:
        return jsonify({
            "sucesso": False,
            "erro": str(e)
        }), 500

@app.route('/relatorios')
def relatorios():
    """Página de relatórios e análises"""
    db = SessionLocal()
    
    try:
        # Relatório por período
        hoje = datetime.now().date()
        mes_atual = hoje.replace(day=1)
        
        # Processos cadastrados no mês
        processos_mes = db.query(Processo).filter(
            Processo.data_cadastro >= mes_atual
        ).count()
        
        # Ofícios baixados no mês
        oficios_mes = db.query(Processo).filter(
            and_(
                Processo.data_busca_oficio >= mes_atual,
                Processo.tem_oficio == True
            )
        ).count()
        
        # Valor total por tribunal
        valor_por_tribunal = db.query(
            Processo.tribunal,
            func.sum(Processo.valor_atualizado).label('total')
        ).group_by(Processo.tribunal).all()
        
        # Top 10 maiores processos
        maiores_processos = db.query(Processo).order_by(
            Processo.valor_atualizado.desc()
        ).limit(10).all()
        
        # Processos por status
        por_status = db.query(
            Processo.status,
            func.count(Processo.id).label('total')
        ).group_by(Processo.status).all()
        
        return render_template('relatorios.html',
            processos_mes=processos_mes,
            oficios_mes=oficios_mes,
            valor_por_tribunal=valor_por_tribunal,
            maiores_processos=maiores_processos,
            por_status=por_status
        )
        
    finally:
        db.close()

@app.route('/contatos')
def contatos():
    """Página de gestão de contatos (leads)"""
    db = SessionLocal()
    
    try:
        busca = request.args.get('busca')
        tipo = request.args.get('tipo')
        
        query = db.query(Contato)
        
        if busca:
            query = query.filter(
                or_(
                    Contato.nome.contains(busca),
                    Contato.email_principal.contains(busca),
                    Contato.telefone_principal.contains(busca)
                )
            )
        
        if tipo:
            query = query.filter(Contato.tipo == tipo)
        
        contatos = query.order_by(Contato.data_cadastro.desc()).all()
        
        return render_template('contatos.html',
            contatos=contatos
        )
        
    finally:
        db.close()

@app.route('/download-oficio/<int:processo_id>')
def download_oficio(processo_id):
    """Download do ofício requisitório"""
    db = SessionLocal()
    
    try:
        processo = db.query(Processo).filter(Processo.id == processo_id).first()
        
        if not processo or not processo.caminho_oficio:
            return "Ofício não encontrado", 404
        
        caminho = Path(processo.caminho_oficio)
        
        if not caminho.exists():
            return "Arquivo não encontrado", 404
        
        return send_file(
            caminho,
            as_attachment=True,
            download_name=f"oficio_{processo.numero_processo.replace('/', '_')}.pdf"
        )
        
    finally:
        db.close()

@app.route('/api/estatisticas')
def api_estatisticas():
    """API para estatísticas em tempo real"""
    db = SessionLocal()
    
    try:
        stats = {
            "total_processos": db.query(Processo).count(),
            "total_valor": float(db.query(func.sum(Processo.valor_atualizado)).scalar() or 0),
            "com_oficio": db.query(Processo).filter(Processo.tem_oficio == True).count(),
            "pendentes": db.query(Processo).filter(Processo.status == StatusProcessoEnum.PENDENTE).count(),
            "em_negociacao": db.query(Processo).filter(Processo.status == StatusProcessoEnum.NEGOCIACAO).count(),
            "concluidos": db.query(Processo).filter(Processo.status == StatusProcessoEnum.CONCLUIDO).count()
        }
        
        return jsonify(stats)
        
    finally:
        db.close()

@app.route('/api/buscar-processo-tjsp', methods=['POST'])
def buscar_processo_tjsp():
    """API para buscar dados de processo no TJSP"""
    try:
        dados = request.json
        numero_processo = dados.get('numero_processo')
        
        # Aqui você integraria com o scraper do TJSP
        # Por enquanto, retorna dados simulados
        
        return jsonify({
            "sucesso": True,
            "dados": {
                "numero_processo": numero_processo,
                "tribunal": "TJSP",
                "classe": "Execução de Título Extrajudicial",
                "assunto": "Precatório",
                "area": "Cível"
            }
        })
        
    except Exception as e:
        return jsonify({
            "sucesso": False,
            "erro": str(e)
        }), 500

# Filtro customizado para formatação de moeda
@app.template_filter('moeda')
def filtro_moeda(valor):
    """Formata valor como moeda brasileira"""
    if valor is None:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Filtro para tamanho de arquivo
@app.template_filter('filesizeformat')
def filtro_tamanho_arquivo(bytes):
    """Formata tamanho de arquivo"""
    if bytes is None:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    
    return f"{bytes:.1f} TB"

# Handler de erro 404
@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template('404.html'), 404

# Handler de erro 500
@app.errorhandler(500)
def erro_interno(e):
    return render_template('500.html'), 500



# ============================================================================
# ROTAS PARA ATUALIZAÇÃO DE OFÍCIO REQUISITÓRIO
# ============================================================================

@app.route('/processo/<int:processo_id>/atualizar-oficio-page')
def atualizar_oficio_page(processo_id):
    """Página de atualização do ofício requisitório"""
    db = SessionLocal()
    
    try:
        processo = db.query(Processo).filter(Processo.id == processo_id).first()
        
        if not processo:
            flash('Processo não encontrado', 'danger')
            return redirect(url_for('listar_processos'))
        
        # Buscar histórico de atualizações
        from sqlalchemy import text
        atualizacoes = db.execute(text("""
            SELECT * FROM atualizacoes_oficio 
            WHERE processo_id = :processo_id 
            ORDER BY data_atualizacao DESC
        """), {"processo_id": processo_id}).fetchall()
        
        # Converter para lista de dicionários
        atualizacoes_list = []
        for row in atualizacoes:
            atualizacoes_list.append({
                'id': row[0],
                'data_atualizacao': datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f') if '.' in row[2] else datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S'),
                'status_anterior': row[3],
                'status_novo': row[4],
                'descricao': row[5],
                'observacoes': row[6],
                'valor_atualizado': row[7],
                'numero_oficio': row[8],
                'numero_precatorio': row[9],
                'origem': row[10],
                'usuario': row[11],
                'validado': row[12]
            })
        
        ultima_atualizacao = atualizacoes_list[0] if atualizacoes_list else None
        
        from datetime import date
        hoje = date.today().isoformat()
        
        return render_template('atualizar_oficio.html',
            processo=processo,
            atualizacoes=atualizacoes_list,
            total_atualizacoes=len(atualizacoes_list),
            ultima_atualizacao=ultima_atualizacao,
            hoje=hoje
        )
        
    finally:
        db.close()

@app.route('/processo/<int:processo_id>/atualizar-oficio', methods=['POST'])
def atualizar_oficio(processo_id):
    """Registra nova atualização do ofício requisitório"""
    db = SessionLocal()
    
    try:
        processo = db.query(Processo).filter(Processo.id == processo_id).first()
        
        if not processo:
            flash('Processo não encontrado', 'danger')
            return redirect(url_for('listar_processos'))
        
        # Dados do formulário
        status_novo = request.form.get('status_novo')
        data_atualizacao = request.form.get('data_atualizacao')
        numero_oficio = request.form.get('numero_oficio')
        numero_precatorio = request.form.get('numero_precatorio')
        valor_atualizado = request.form.get('valor_atualizado', type=float)
        origem = request.form.get('origem')
        descricao = request.form.get('descricao')
        observacoes = request.form.get('observacoes')
        
        # Status anterior
        from sqlalchemy import text
        status_anterior = db.execute(text("""
            SELECT status_oficio FROM processos WHERE id = :id
        """), {"id": processo_id}).scalar()
        
        # Registrar atualização
        db.execute(text("""
            INSERT INTO atualizacoes_oficio 
            (processo_id, data_atualizacao, status_anterior, status_novo, 
             descricao, observacoes, valor_atualizado, numero_oficio, 
             numero_precatorio, origem, usuario, validado)
            VALUES 
            (:processo_id, :data_atualizacao, :status_anterior, :status_novo,
             :descricao, :observacoes, :valor_atualizado, :numero_oficio,
             :numero_precatorio, :origem, :usuario, :validado)
        """), {
            "processo_id": processo_id,
            "data_atualizacao": datetime.now(),
            "status_anterior": status_anterior,
            "status_novo": status_novo,
            "descricao": descricao,
            "observacoes": observacoes,
            "valor_atualizado": valor_atualizado,
            "numero_oficio": numero_oficio,
            "numero_precatorio": numero_precatorio,
            "origem": origem,
            "usuario": "Sistema",  # Aqui você pode pegar do login
            "validado": True if origem in ['PORTAL_TRIBUNAL', 'DIARIO_OFICIAL'] else False
        })
        
        # Atualizar processo
        db.execute(text("""
            UPDATE processos 
            SET status_oficio = :status_novo,
                data_ultima_atualizacao_oficio = :data_atualizacao,
                numero_oficio = COALESCE(:numero_oficio, numero_oficio)
            WHERE id = :id
        """), {
            "status_novo": status_novo,
            "data_atualizacao": datetime.now(),
            "numero_oficio": numero_oficio,
            "id": processo_id
        })
        
        # Atualizar valor se fornecido
        if valor_atualizado:
            db.execute(text("""
                UPDATE processos 
                SET valor_atualizado = :valor
                WHERE id = :id
            """), {
                "valor": valor_atualizado,
                "id": processo_id
            })
        
        db.commit()
        
        flash('Atualização do ofício registrada com sucesso!', 'success')
        return redirect(url_for('atualizar_oficio_page', processo_id=processo_id))
        
    except Exception as e:
        db.rollback()
        flash(f'Erro ao registrar atualização: {str(e)}', 'danger')
        return redirect(url_for('atualizar_oficio_page', processo_id=processo_id))
    finally:
        db.close()





# ============================================================================
# ROTAS PARA BUSCA EM LISTAS DE PRECATÓRIOS PENDENTES
# ============================================================================

@app.route('/buscar-listas-precatorios')
def buscar_listas_precatorios():
    """Página de busca em listas de precatórios pendentes"""
    return render_template('buscar_listas_precatorios.html')

@app.route('/buscar-listas-precatorios/executar', methods=['POST'])
def executar_busca_listas():
    """Executa busca nas listas de precatórios"""
    db = SessionLocal()
    
    try:
        # Parâmetros do formulário
        tribunal = request.form.get('tribunal')
        ano = request.form.get('ano', type=int)
        natureza = request.form.get('natureza')
        valor_min = request.form.get('valor_min', type=float)
        valor_max = request.form.get('valor_max', type=float)
        apenas_prioritarios = request.form.get('apenas_prioritarios') == 'on'
        
        # Simular busca (em produção, aqui seria o scraper real)
        import time
        import random
        
        # Aguardar alguns segundos (simulando busca)
        time.sleep(2)
        
        # Gerar resultados simulados
        resultados = []
        num_resultados = random.randint(5, 15)
        
        for i in range(num_resultados):
            valor = random.uniform(
                valor_min if valor_min else 100000,
                valor_max if valor_max else 5000000
            )
            
            resultado = {
                'numero_processo': f"000{i+1:04d}-{random.randint(10,99)}.{ano}.8.26.0053",
                'credor': f"Credor Exemplo {i+1}",
                'valor': valor,
                'natureza': natureza if natureza else random.choice(['ALIMENTAR', 'COMUM', 'TRIBUTARIO']),
                'ano': ano,
                'tribunal': tribunal,
                'prioritario': apenas_prioritarios or random.choice([True, False])
            }
            resultados.append(resultado)
        
        # Renderizar página de resultados
        return render_template('resultados_busca_listas.html',
            resultados=resultados,
            tribunal=tribunal,
            ano=ano,
            total=len(resultados),
            valor_total=sum(r['valor'] for r in resultados)
        )
        
    except Exception as e:
        flash(f'Erro ao executar busca: {str(e)}', 'danger')
        return redirect(url_for('buscar_listas_precatorios'))
    finally:
        db.close()





# Rota para dashboard moderno
@app.route('/dashboard-moderno')
def dashboard_moderno():
    """Dashboard moderno baseado no modelo poker-tool"""
    return render_template('dashboard_moderno.html')

# API para dados do dashboard
@app.route('/api/processos')
def api_processos():
    """API para retornar dados dos processos"""
    db = SessionLocal()
    try:
        processos = db.query(Processo).all()
        
        dados = []
        for p in processos:
            dados.append({
                'id': p.id,
                'numero': p.numero_processo,
                'tribunal': p.tribunal.value if p.tribunal else '',
                'credor': p.credor_nome,
                'valor': float(p.valor_atualizado) if p.valor_atualizado else 0,
                'natureza': p.natureza.value if p.natureza else '',
                'status': p.status.value if p.status else '',
                'situacao': 'Pago' if p.status and p.status.name == 'PAGO' else 
                           'Pronto Não Pago' if not p.possui_pendencia_pagamento else 
                           'Com Pendência',
                'temOficio': p.tem_oficio,
                'prioritario': p.credor_idoso or p.credor_doenca_grave or p.credor_deficiente
            })
        
        return jsonify(dados)
    finally:
        db.close()





# ============================================================================
# ROTAS PARA ATUALIZAÇÃO DE VALORES E CALCULADORA
# ============================================================================

@app.route('/processo/<int:processo_id>/atualizar-valores')
def atualizar_valores_page(processo_id):
    """Página de atualização de valores"""
    db = SessionLocal()
    
    try:
        processo = db.query(Processo).filter(Processo.id == processo_id).first()
        
        if not processo:
            flash('Processo não encontrado', 'danger')
            return redirect(url_for('listar_processos'))
        
        # Buscar histórico
        from sqlalchemy import text
        historico = db.execute(text("""
            SELECT * FROM historico_valores 
            WHERE processo_id = :processo_id 
            ORDER BY data_atualizacao DESC
        """), {"processo_id": processo_id}).fetchall()
        
        # Converter para lista de dicionários
        historico_list = []
        for row in historico:
            historico_list.append({
                'data_atualizacao': datetime.strptime(str(row[2]), '%Y-%m-%d %H:%M:%S.%f') if '.' in str(row[2]) else datetime.strptime(str(row[2]), '%Y-%m-%d %H:%M:%S'),
                'valor_principal': row[3],
                'valor_juros': row[4],
                'valor_correcao': row[5],
                'valor_total': row[6],
                'taxa_juros': row[7],
                'indice_correcao': row[8],
                'periodo_inicio': datetime.strptime(str(row[9]), '%Y-%m-%d') if row[9] else None,
                'periodo_fim': datetime.strptime(str(row[10]), '%Y-%m-%d') if row[10] else None
            })
        
        from datetime import date
        hoje = date.today().isoformat()
        
        return render_template('atualizar_valores.html',
            processo=processo,
            historico=historico_list,
            hoje=hoje
        )
        
    finally:
        db.close()

@app.route('/api/calcular-valores', methods=['POST'])
def api_calcular_valores():
    """API para calcular valores"""
    try:
        data = request.get_json()
        
        # Importar calculadora
        import sys
        sys.path.append('src')
        from calculadora_juros import CalculadoraPrecatorio
        
        # Criar calculadora
        calc = CalculadoraPrecatorio(
            valor_principal=data['valor_principal'],
            data_base=data['data_base'],
            data_final=data['data_final'],
            taxa_juros_mensal=data['taxa_juros'],
            indice_correcao=data['indice_correcao']
        )
        
        # Calcular
        resultado = calc.calcular_tudo(tipo_juros=data.get('tipo_juros', 'SIMPLES'))
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/detalhamento-mensal', methods=['POST'])
def api_detalhamento_mensal():
    """API para detalhamento mensal"""
    try:
        data = request.get_json()
        
        # Importar calculadora
        import sys
        sys.path.append('src')
        from calculadora_juros import CalculadoraPrecatorio
        
        # Criar calculadora
        calc = CalculadoraPrecatorio(
            valor_principal=data['valor_principal'],
            data_base=data['data_base'],
            data_final=data['data_final'],
            taxa_juros_mensal=data['taxa_juros'],
            indice_correcao=data['indice_correcao']
        )
        
        # Gerar detalhamento
        detalhes = calc.gerar_detalhamento_mensal()
        
        return jsonify(detalhes)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/processo/<int:processo_id>/salvar-atualizacao-valores', methods=['POST'])
def salvar_atualizacao_valores(processo_id):
    """Salva atualização de valores"""
    db = SessionLocal()
    
    try:
        processo = db.query(Processo).filter(Processo.id == processo_id).first()
        
        if not processo:
            return jsonify({'success': False, 'error': 'Processo não encontrado'}), 404
        
        data = request.get_json()
        
        # Salvar no histórico
        from sqlalchemy import text
        db.execute(text("""
            INSERT INTO historico_valores 
            (processo_id, data_atualizacao, valor_principal, valor_juros, 
             valor_correcao, valor_total, taxa_juros, indice_correcao, 
             periodo_inicio, periodo_fim, usuario)
            VALUES 
            (:processo_id, :data_atualizacao, :valor_principal, :valor_juros,
             :valor_correcao, :valor_total, :taxa_juros, :indice_correcao,
             :periodo_inicio, :periodo_fim, :usuario)
        """), {
            "processo_id": processo_id,
            "data_atualizacao": datetime.now(),
            "valor_principal": data['valor_principal'],
            "valor_juros": data['valor_juros'],
            "valor_correcao": data['valor_correcao'],
            "valor_total": data['valor_total'],
            "taxa_juros": data['taxa_juros_mensal'],
            "indice_correcao": data['indice_correcao'],
            "periodo_inicio": datetime.strptime(data['data_base'], '%d/%m/%Y').date(),
            "periodo_fim": datetime.strptime(data['data_final'], '%d/%m/%Y').date(),
            "usuario": "Sistema"
        })
        
        # Atualizar processo
        db.execute(text("""
            UPDATE processos 
            SET valor_principal = :valor_principal,
                valor_juros = :valor_juros,
                valor_correcao_monetaria = :valor_correcao,
                valor_atualizado = :valor_total,
                taxa_juros_mensal = :taxa_juros,
                indice_correcao = :indice_correcao,
                data_ultima_atualizacao_valor = :data_atualizacao
            WHERE id = :id
        """), {
            "valor_principal": data['valor_principal'],
            "valor_juros": data['valor_juros'],
            "valor_correcao": data['valor_correcao'],
            "valor_total": data['valor_total'],
            "taxa_juros": data['taxa_juros_mensal'],
            "indice_correcao": data['indice_correcao'],
            "data_atualizacao": datetime.now(),
            "id": processo_id
        })
        
        db.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        db.close()





# API para automação
@app.route('/api/executar-automacao', methods=['POST'])
def api_executar_automacao():
    """API para executar automação"""
    try:
        data = request.get_json()
        tipo = data.get('tipo')
        tribunal = data.get('tribunal')
        processos = data.get('processos')
        
        # Simular execução (implementar lógica real depois)
        import time
        import random
        
        time.sleep(3)  # Simular processamento
        
        resultado = {
            'success': True,
            'tipo': tipo,
            'tribunal': tribunal,
            'processados': random.randint(5, 20),
            'sucesso': random.randint(4, 18),
            'erros': random.randint(0, 2),
            'tempo': 3
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500





# ============================================================================
# APIs PARA CALCULADORA DE PRECATÓRIOS
# ============================================================================

from flask import jsonify
import sys
sys.path.append('src')

@app.route('/api/calcular-valores', methods=['POST'])
def api_calcular_valores():
    """
    API para calcular valores de precatórios
    
    Request JSON:
        - valor_principal: float
        - data_base: string (YYYY-MM-DD)
        - data_final: string (YYYY-MM-DD)
        - taxa_juros: float (%)
        - indice_correcao: string (IPCA, INPC, TR, SELIC)
        - tipo_juros: string (SIMPLES ou COMPOSTOS)
    
    Response JSON:
        - valor_principal: float
        - valor_juros: float
        - valor_correcao: float
        - valor_total: float
        - meses_calculados: int
        - taxa_juros_mensal: float
        - indice_correcao: string
        - tipo_juros: string
        - data_base: string
        - data_final: string
    """
    try:
        data = request.get_json()
        
        # Importar calculadora
        from calculadora_precatorios import CalculadoraPrecatorioCompleta
        
        # Criar e configurar calculadora
        calc = CalculadoraPrecatorioCompleta()
        calc.configurar(
            valor_principal=data['valor_principal'],
            data_base=data['data_base'],
            data_final=data.get('data_final'),
            taxa_juros_mensal=data.get('taxa_juros', 0.5),
            indice_correcao=data.get('indice_correcao', 'IPCA'),
            tipo_juros=data.get('tipo_juros', 'SIMPLES')
        )
        
        # Calcular
        resultado = calc.calcular_tudo()
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Erro ao calcular valores'
        }), 500

@app.route('/api/detalhamento-mensal', methods=['POST'])
def api_detalhamento_mensal():
    """
    API para gerar detalhamento mensal
    
    Request JSON:
        - valor_principal: float
        - data_base: string (YYYY-MM-DD)
        - data_final: string (YYYY-MM-DD)
        - taxa_juros: float (%)
        - indice_correcao: string (IPCA, INPC, TR, SELIC)
    
    Response JSON:
        Array de objetos com:
        - mes: string (MM/YYYY)
        - valor_inicial: float
        - juros: float
        - correcao: float
        - valor_final: float
    """
    try:
        data = request.get_json()
        
        # Importar calculadora
        from calculadora_precatorios import CalculadoraPrecatorioCompleta
        
        # Criar e configurar calculadora
        calc = CalculadoraPrecatorioCompleta()
        calc.configurar(
            valor_principal=data['valor_principal'],
            data_base=data['data_base'],
            data_final=data.get('data_final'),
            taxa_juros_mensal=data.get('taxa_juros', 0.5),
            indice_correcao=data.get('indice_correcao', 'IPCA')
        )
        
        # Gerar detalhamento
        detalhes = calc.gerar_detalhamento_mensal()
        
        return jsonify(detalhes)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Erro ao gerar detalhamento'
        }), 500

@app.route('/api/teste-calculadora', methods=['GET'])
def api_teste_calculadora():
    """API para testar a calculadora"""
    try:
        from calculadora_precatorios import CalculadoraPrecatorioCompleta
        
        calc = CalculadoraPrecatorioCompleta()
        calc.configurar(
            valor_principal=100000.00,
            data_base='2020-01-01',
            data_final='2026-01-06',
            taxa_juros_mensal=0.5,
            indice_correcao='IPCA',
            tipo_juros='SIMPLES'
        )
        
        resultado = calc.calcular_tudo()
        
        return jsonify({
            'status': 'OK',
            'message': 'Calculadora funcionando corretamente',
            'exemplo': resultado
        })
        
    except Exception as e:
        return jsonify({
            'status': 'ERRO',
            'message': str(e)
        }), 500



# Configuracao para Railway/Heroku
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
    print("\n" + "="*60)
    print("TAX MASTER - DASHBOARD WEB")
    print("Sistema de Gestão de Precatórios")
    print("Versão 2.0 - Com Processo Principal/Conhecimento")
    print("="*60)
    print("\nRecursos:")
    print("- Cadastro com 2 campos de processo")
    print("- Automação inteligente de busca de ofícios")
    print("- Filtros avançados e relatórios")
    print("- Gestão completa de contatos")
    print("="*60)
    print("\nIniciando servidor...")
    print("Acesse: http://localhost:8080")
    print("\nPressione Ctrl+C para parar")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=8080)


