import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import time
import random
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import sys
import requests
from datetime import datetime
from collections import Counter, defaultdict
import threading

try:
    import numpy as np
    from scipy import stats
    from scipy.special import comb
    NUMPY_DISPONIVEL = True
except ImportError:
    NUMPY_DISPONIVEL = False
    import math
    def comb(n, k, exact=True):
        resultado = math.factorial(n) // (math.factorial(k) * math.factorial(n - k))
        return resultado if exact else float(resultado)

# Constantes
TOTAL_DEZENAS = 25
TOTAL_COMBINACOES = 3268760
VERSAO = "6.0 ULTIMATE"

TIPOS_JOGOS = {
    15: {'dezenas': 15, 'apostas': 1, 'custo': 3.00, 'nome': 'Simples (15 números)'},
    16: {'dezenas': 16, 'apostas': 16, 'custo': 48.00, 'nome': 'Desdobramento (16 números)'},
    17: {'dezenas': 17, 'apostas': 68, 'custo': 204.00, 'nome': 'Desdobramento (17 números)'},
    18: {'dezenas': 18, 'apostas': 204, 'custo': 612.00, 'nome': 'Desdobramento (18 números)'}
}

PREMIOS_MEDIOS = {15: 1800000.00, 14: 2000.00, 13: 30.00, 12: 12.00, 11: 6.00}

# Splash Screen
def mostrar_splash():
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.attributes('-topmost', True)
    
    largura = 750
    altura = 500
    x = (splash.winfo_screenwidth() - largura) // 2
    y = (splash.winfo_screenheight() - altura) // 2
    splash.geometry(f"{largura}x{altura}+{x}+{y}")
    
    frame = tk.Frame(splash, bg="#0A0E27")
    frame.pack(fill="both", expand=True)
    
    header = tk.Frame(frame, bg="#6A0DAD", height=130)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    tk.Label(header, text="🔬", font=("Segoe UI Emoji", 75), bg="#6A0DAD", fg="#FFD700").pack(pady=20)
    tk.Label(frame, text="LOTOFÁCIL QUANTUM", font=("Segoe UI", 42, "bold"), bg="#0A0E27", fg="#FFD700").pack(pady=20)
    tk.Label(frame, text="ULTIMATE PRO EDITION", font=("Segoe UI", 14, "bold"), bg="#0A0E27", fg="#00D9FF").pack()
    tk.Label(frame, text=f"v{VERSAO} OTIMIZADO - Robinson", font=("Segoe UI", 9), bg="#0A0E27", fg="#707070").pack(pady=5)
    
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Ultimate.Horizontal.TProgressbar", troughcolor='#1C1C1C', background='#FFD700', thickness=24)
    
    progress = ttk.Progressbar(frame, length=650, mode='determinate', style="Ultimate.Horizontal.TProgressbar")
    progress.pack(pady=30)
    
    label_status = tk.Label(frame, text="Inicializando...", font=("Segoe UI", 11, "bold"), bg="#0A0E27", fg="#FFFFFF")
    label_status.pack(pady=10)
    
    etapas = [
        (0, 20, "🔬 Inicializando núcleo..."),
        (20, 40, "🤖 Carregando IA..."),
        (40, 60, "📊 Preparando análise..."),
        (60, 80, "🎲 Calibrando..."),
        (80, 100, "✅ Pronto!")
    ]
    
    for inicio, fim, texto in etapas:
        label_status.config(text=texto)
        for i in range(inicio, fim + 1):
            progress['value'] = i
            splash.update()
            time.sleep(0.008)
    
    time.sleep(0.3)
    splash.destroy()

# Machine Learning Simples
class MachineLearningSimples:
    def __init__(self):
        self.pesos = {}
    
    def treinar(self, historico):
        if not historico:
            return
        
        for i, resultado in enumerate(historico):
            peso_temporal = (i + 1) / len(historico)
            for dezena in resultado['dezenas']:
                if dezena not in self.pesos:
                    self.pesos[dezena] = 0
                self.pesos[dezena] += peso_temporal
        
        total = sum(self.pesos.values())
        if total > 0:
            self.pesos = {d: (p / total) * 100 for d, p in self.pesos.items()}
    
    def prever_scores(self):
        return self.pesos if self.pesos else {d: 50.0 for d in range(1, 26)}

# Calculadora de Probabilidades
class CalculadoraProbabilidades:
    @staticmethod
    def calcular_prob_simples(acertos):
        if acertos < 11 or acertos > 15:
            return 0.0
        return (comb(15, acertos, exact=True) * comb(10, 15-acertos, exact=True)) / TOTAL_COMBINACOES
    
    @staticmethod
    def calcular_prob_desdobramento(num_dez, acertos):
        if acertos < 11 or acertos > 15:
            return 0.0
        num_apostas = comb(num_dez, 15, exact=True)
        prob_uma = CalculadoraProbabilidades.calcular_prob_simples(acertos)
        if acertos >= 14:
            return min(num_apostas * prob_uma, 1.0)
        return 1 - (1 - prob_uma) ** num_apostas
    
    @staticmethod
    def calcular_todas_prob(jogo, tipo_jogo=15):
        num_dez = len(jogo)
        probs = {}
        if tipo_jogo == 15 or num_dez == 15:
            for a in range(11, 16):
                probs[a] = CalculadoraProbabilidades.calcular_prob_simples(a)
        else:
            for a in range(11, 16):
                probs[a] = CalculadoraProbabilidades.calcular_prob_desdobramento(num_dez, a)
        return probs
    
    @staticmethod
    def calcular_ev(jogo, tipo_jogo=15):
        probs = CalculadoraProbabilidades.calcular_todas_prob(jogo, tipo_jogo)
        custo = TIPOS_JOGOS[tipo_jogo]['custo']
        ev = sum(PREMIOS_MEDIOS.get(a, 0) * probs[a] for a in range(11, 16))
        return ev, ev - custo
    
    @staticmethod
    def calcular_roi(jogo, tipo_jogo=15):
        _, ev_liq = CalculadoraProbabilidades.calcular_ev(jogo, tipo_jogo)
        return (ev_liq / TIPOS_JOGOS[tipo_jogo]['custo']) * 100
# Analisador Ultimate OTIMIZADO
class AnalisadorUltimate:
    def __init__(self):
        self.historico = []
        self.matriz_frequencia = [0] * 26
        self.matriz_gaps = defaultdict(list)
        self.matriz_pares = defaultdict(int)
        self.ml_model = MachineLearningSimples()
        self.ultima_atualizacao = None
        self.estatisticas_avancadas = {}
    
    def carregar_historico_maximo(self, max_concursos=100, callback=None):
        """Carrega histórico com retry e feedback"""
        try:
            url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/"
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            if callback:
                callback(f"📥 Conectando à API...")
            
            # Conexão inicial
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                return False
            
            dados = response.json()
            ultimo = dados.get('numero', 0)
            
            if callback:
                callback(f"📥 Baixando {max_concursos} concursos...")
            
            progresso = 0
            erros = 0
            max_erros = 15
            
            for i in range(min(max_concursos, ultimo)):
                num = ultimo - i
                
                # Sistema de retry (3 tentativas)
                for tentativa in range(3):
                    try:
                        resp = requests.get(f"{url}{num}", headers=headers, timeout=15)
                        if resp.status_code == 200:
                            d = resp.json()
                            dezenas = sorted([int(x) for x in d.get('listaDezenas', [])])
                            
                            self.historico.append({
                                'concurso': num,
                                'data': d.get('dataApuracao'),
                                'dezenas': dezenas
                            })
                            
                            progresso += 1
                            
                            # Feedback a cada 10 concursos
                            if progresso % 10 == 0 and callback:
                                callback(f"📥 Carregados: {progresso}/{max_concursos}")
                            
                            break
                        else:
                            raise Exception(f"Status {resp.status_code}")
                            
                    except Exception as e:
                        if tentativa < 2:
                            time.sleep(1)
                            continue
                        else:
                            erros += 1
                            if erros >= max_erros:
                                break
                
                time.sleep(0.3)  # Delay para evitar rate limit
                
                if erros >= max_erros:
                    break
            
            if len(self.historico) < 30:
                return False
            
            self.historico.reverse()
            self.ultima_atualizacao = datetime.now()
            
            if callback:
                callback("🧮 Calculando estatísticas...")
            
            self._calcular_tudo()
            
            if callback:
                callback("🤖 Treinando ML...")
            
            self.ml_model.treinar(self.historico)
            
            return True
            
        except Exception as e:
            return False
    
    def _calcular_tudo(self):
        if not self.historico:
            return
        
        for r in self.historico:
            for d in r['dezenas']:
                self.matriz_frequencia[d] += 1
        
        ultima = {i: -1 for i in range(1, 26)}
        for idx, r in enumerate(self.historico):
            for d in range(1, 26):
                if d in r['dezenas']:
                    if ultima[d] >= 0:
                        self.matriz_gaps[d].append(idx - ultima[d])
                    ultima[d] = idx
        
        for r in self.historico:
            dez = r['dezenas']
            for i in range(len(dez)):
                for j in range(i + 1, len(dez)):
                    self.matriz_pares[tuple(sorted([dez[i], dez[j]]))] += 1
    
    def calcular_score_ultimate(self, dezena):
        score = 0.0
        
        # Frequência (25%)
        total = sum(self.matriz_frequencia)
        if total > 0:
            freq = self.matriz_frequencia[dezena] / total
            score += (freq / (1/25)) * 25
        
        # ML Score (20%)
        ml_scores = self.ml_model.prever_scores()
        score += (ml_scores.get(dezena, 50) / 100) * 20
        
        # Tendência recente (20%)
        ultimos_25 = [r['dezenas'] for r in self.historico[-25:]]
        freq_25 = sum(1 for j in ultimos_25 if dezena in j)
        score += (freq_25 / 25) * 100 * 0.20
        
        # Gap (20%)
        if dezena in self.matriz_gaps and self.matriz_gaps[dezena]:
            if NUMPY_DISPONIVEL:
                gap_medio = np.mean(self.matriz_gaps[dezena])
            else:
                gap_medio = sum(self.matriz_gaps[dezena]) / len(self.matriz_gaps[dezena])
            
            gap_atual = len(self.historico) - max([i for i, r in enumerate(self.historico) if dezena in r['dezenas']], default=0)
            if gap_atual > gap_medio:
                score += min((gap_atual / gap_medio) * 20, 30)
        
        # Posição (10%)
        score += (1 - abs(dezena - 13) / 12) * 10
        
        # Paridade (5%)
        total_jogos = len(self.historico)
        if total_jogos > 0:
            if dezena % 2 == 0:
                count = sum(1 for r in self.historico for d in r['dezenas'] if d % 2 == 0)
            else:
                count = sum(1 for r in self.historico for d in r['dezenas'] if d % 2 != 0)
            score += (count / (total_jogos * 15)) * 5
        
        return round(score, 2)
    
    def calcular_scores_todos(self):
        return {d: self.calcular_score_ultimate(d) for d in range(1, 26)}
    
    def gerar_jogos_otimizados(self, scores, tipo_jogo, qtd):
        num_dez = TIPOS_JOGOS[tipo_jogo]['dezenas']
        top_dezenas = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:num_dez+8]
        
        jogos = []
        jogos_set = set()
        
        tentativas = 0
        max_tentativas = qtd * 100
        
        while len(jogos) < qtd and tentativas < max_tentativas:
            tentativas += 1
            
            # 80% top scores, 20% variação
            if random.random() < 0.8:
                candidatas = [d for d, s in top_dezenas[:num_dez+3]]
            else:
                candidatas = [d for d, s in top_dezenas]
            
            if len(candidatas) >= num_dez:
                jogo = sorted(random.sample(candidatas, num_dez))
                jogo_tuple = tuple(jogo)
                
                if jogo_tuple not in jogos_set:
                    jogos.append(jogo)
                    jogos_set.add(jogo_tuple)
        
        return jogos
# Instâncias Globais
analisador = AnalisadorUltimate()
calc_prob = CalculadoraProbabilidades()

# Funções da Interface
def atualizar_info_tipo(*args):
    tipo = combo_tipo.get()
    tipo_num = int(tipo.split()[0])
    info = TIPOS_JOGOS[tipo_num]
    texto_info_jogo.set(f"💰 R$ {info['custo']:.2f} | 🎲 {info['apostas']} aposta{'s' if info['apostas'] > 1 else ''}")

def buscar_analisar_ultimate():
    """Análise com janela de progresso"""
    
    # Janela de progresso
    janela_prog = tk.Toplevel(root)
    janela_prog.title("⏳ Análise ULTIMATE")
    janela_prog.geometry("500x250")
    janela_prog.transient(root)
    janela_prog.grab_set()
    
    tk.Label(janela_prog, text="📥 Carregando Análise ULTIMATE", font=("Arial", 14, "bold")).pack(pady=20)
    
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(janela_prog, length=400, mode='indeterminate', variable=progress_var)
    progress_bar.pack(pady=10)
    progress_bar.start(10)
    
    label_prog = tk.Label(janela_prog, text="Iniciando...", font=("Arial", 10))
    label_prog.pack(pady=10)
    
    def atualizar_status(msg):
        label_prog.config(text=msg)
        janela_prog.update()
    
    def task():
        try:
            if not analisador.carregar_historico_maximo(100, callback=atualizar_status):
                janela_prog.destroy()
                messagebox.showerror("Erro", 
                    "Falha ao carregar histórico.\n\n"
                    "Possíveis causas:\n"
                    "• Problema de conexão\n"
                    "• Firewall/Antivírus bloqueando\n"
                    "• API temporariamente indisponível\n\n"
                    "Tente novamente em alguns minutos.")
                texto_status.set("❌ Falha ao carregar.")
                return
            
            scores = analisador.calcular_scores_todos()
            
            janela_prog.destroy()
            exibir_dashboard_simples(scores)
            
            texto_status.set(f"✅ {len(analisador.historico)} concursos analisados!")
            
        except Exception as e:
            janela_prog.destroy()
            messagebox.showerror("Erro", f"Erro:\n{str(e)}")
    
    thread = threading.Thread(target=task, daemon=True)
    thread.start()

def exibir_dashboard_simples(scores):
    """Dashboard simplificado com CORES"""
    janela = tk.Toplevel(root)
    janela.title("🏆 Ranking ULTIMATE")
    janela.geometry("800x600")
    janela.configure(bg="#1a1a2e")
    
    tk.Label(janela, text="🏆 RANKING DE DEZENAS", 
             font=("Arial", 14, "bold"), 
             bg="#1a1a2e", fg="#FFD700").pack(pady=10)
    
    text = scrolledtext.ScrolledText(janela, 
                                     font=("Courier", 10), 
                                     bg="#0f0f1e", 
                                     fg="#FFFFFF",
                                     insertbackground="#FFD700")
    text.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Configurar tags de cores
    text.tag_config("header", foreground="#FFD700", font=("Courier", 10, "bold"))
    text.tag_config("ultra", foreground="#FF4444", font=("Courier", 10, "bold"))
    text.tag_config("quente", foreground="#FF9500", font=("Courier", 10, "bold"))
    text.tag_config("neutro", foreground="#FFC107", font=("Courier", 10))
    text.tag_config("frio", foreground="#03A9F4", font=("Courier", 10))
    
    ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Cabeçalho com cor
    text.insert("end", f"{'#':<4} {'DEZ':<6} {'SCORE':<10} {'VISUAL':<30} {'STATUS'}\n", "header")
    text.insert("end", "="*70 + "\n\n", "header")
    
    for idx, (dez, score) in enumerate(ranking, 1):
        barra = "█" * int((score / 100) * 25)
        
        # Determinar status e cor
        if score >= 80:
            status = "🔥 ULTRA"
            tag = "ultra"
        elif score >= 70:
            status = "🌡️ QUENTE"
            tag = "quente"
        elif score >= 50:
            status = "➡️ NEUTRO"
            tag = "neutro"
        else:
            status = "❄️ FRIO"
            tag = "frio"
        
        # Inserir linha com cor
        linha = f"{idx:<4} {dez:02d}     {score:<10.1f} {barra:<30} {status}\n"
        text.insert("end", linha, tag)
    
    text.config(state="disabled")
    
    # Botões com cores
    frame_btn = tk.Frame(janela, bg="#1a1a2e")
    frame_btn.pack(pady=10)
    
    tk.Button(frame_btn, text="🎯 Usar Top 10", 
              command=lambda: usar_top([d for d, s in ranking[:10]]), 
              bg="#4CAF50", fg="white", 
              font=("Arial", 10, "bold"), 
              padx=15, pady=8).pack(side="left", padx=5)
    
    tk.Button(frame_btn, text="❌ Fechar", 
              command=janela.destroy, 
              bg="#FF5722", fg="white", 
              font=("Arial", 10, "bold"),
              padx=15, pady=8).pack(side="left", padx=5)
def usar_top(dezenas):
    entry_fixas.delete(0, "end")
    entry_fixas.insert(0, " ".join(map(str, dezenas)))
    messagebox.showinfo("✅", f"Top {len(dezenas)} aplicadas!")
    texto_status.set(f"✨ Top {len(dezenas)} configuradas!")

def gerar_jogos_ultimate():
    try:
        if not analisador.historico:
            if messagebox.askyesno("Análise", "Carregar histórico? (~1 min)"):
                buscar_analisar_ultimate()
                return
            else:
                return
        
        qtd = int(entry_qtd.get())
        if qtd <= 0 or qtd > 50:
            messagebox.showerror("Erro", "Quantidade: 1-50")
            return
        
        tipo_str = combo_tipo.get()
        tipo_jogo = int(tipo_str.split()[0])
        
        texto_status.set(f"🎲 Gerando {qtd} jogos...")
        root.update()
        
        scores = analisador.calcular_scores_todos()
        jogos = analisador.gerar_jogos_otimizados(scores, tipo_jogo, qtd)
        
        jogos_info = []
        for jogo in jogos:
            probs = calc_prob.calcular_todas_prob(jogo, tipo_jogo)
            ev, ev_liq = calc_prob.calcular_ev(jogo, tipo_jogo)
            roi = calc_prob.calcular_roi(jogo, tipo_jogo)
            qualidade = sum(scores.get(d, 50) for d in jogo) / len(jogo)
            
            jogos_info.append({
                'jogo': jogo,
                'tipo': tipo_jogo,
                'probs': probs,
                'ev': ev,
                'ev_liq': ev_liq,
                'roi': roi,
                'qualidade': qualidade
            })
        
        lista_jogos.clear()
        lista_jogos.extend(jogos_info)
        atualizar_preview()
        
        custo = len(jogos) * TIPOS_JOGOS[tipo_jogo]['custo']
        texto_status.set(f"✅ {len(jogos)} jogos | R$ {custo:,.2f}")
        messagebox.showinfo("✅", f"{len(jogos)} jogos gerados!")
        
    except ValueError:
        messagebox.showerror("Erro", "Valor inválido")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def atualizar_preview():
    text_preview.config(state="normal")
    text_preview.delete("1.0", "end")
    
    if not lista_jogos:
        text_preview.insert("1.0", "Aguardando jogos...")
        text_preview.config(state="disabled")
        return
    
    text_preview.insert("end", "JOGOS ULTIMATE GERADOS\n" + "="*80 + "\n\n")
    
    for i, info in enumerate(lista_jogos[:20], 1):
        jogo = info['jogo']
        probs = info['probs']
        dez_str = ' - '.join(f'{d:02d}' for d in jogo)
        text_preview.insert("end", f"{i:02d}: {dez_str}\n")
        text_preview.insert("end", f"    Q:{info['qualidade']:.1f} P(15):{probs[15]*100:.6f}% P(14):{probs[14]*100:.4f}% ROI:{info['roi']:+.1f}%\n\n")
    
    if len(lista_jogos) > 20:
        text_preview.insert("end", f"... e mais {len(lista_jogos)-20} jogos.\n")
    
    text_preview.config(state="disabled")

def salvar_excel():
    if not lista_jogos:
        messagebox.showwarning("Aviso", "Nenhum jogo.")
        return
    
    try:
        caminho = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=f"Lotofacil_ULTIMATE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        if not caminho:
            return
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Jogos ULTIMATE"
        
        tipo = lista_jogos[0]['tipo']
        max_dez = TIPOS_JOGOS[tipo]['dezenas']
        
        headers = ["#"] + [f"D{i}" for i in range(1, max_dez + 1)] + ["Q", "P(15)", "P(14)", "ROI%"]
        ws.append(headers)
        
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="6A0DAD", fill_type="solid")
        
        for i, info in enumerate(lista_jogos, 1):
            linha = [i] + info['jogo'] + [None]*(max_dez-len(info['jogo'])) + [
                round(info['qualidade'], 1),
                f"{info['probs'][15]*100:.6f}%",
                f"{info['probs'][14]*100:.4f}%",
                f"{info['roi']:+.1f}%"
            ]
            ws.append(linha)
        
        wb.save(caminho)
        messagebox.showinfo("✅", "Excel salvo!")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def salvar_pdf():
    if not lista_jogos:
        messagebox.showwarning("Aviso", "Nenhum jogo.")
        return
    
    try:
        caminho = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"Lotofacil_ULTIMATE_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        if not caminho:
            return
        
        c = canvas.Canvas(caminho, pagesize=A4)
        w, h = A4
        y = h - 40
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "JOGOS ULTIMATE")
        y -= 20
        
        c.setFont("Courier", 7)
        for i, info in enumerate(lista_jogos, 1):
            dez_str = ' - '.join(f'{d:02d}' for d in info['jogo'])
            c.drawString(50, y, f"{i:02d}: {dez_str} | ROI:{info['roi']:+.1f}%")
            y -= 10
            if y < 50:
                c.showPage()
                y = h - 40
        
        c.save()
        messagebox.showinfo("✅", "PDF salvo!")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def limpar():
    if lista_jogos and not messagebox.askyesno("Confirmar", "Limpar?"):
        return
    lista_jogos.clear()
    atualizar_preview()
    texto_status.set("Pronto.")

def criar_interface():
    global root, entry_qtd, combo_tipo, entry_fixas, entry_descartadas
    global texto_status, texto_info_jogo, text_preview, lista_jogos
    
    lista_jogos = []
    
    root = tk.Tk()
    root.title(f"🔬 Lotofácil QUANTUM ULTIMATE v{VERSAO}")
    root.geometry("1200x800")
    
    try:
        if os.path.exists("icone_trevo.ico"):
            root.iconbitmap("icone_trevo.ico")
    except:
        pass
    
    main = tk.Frame(root, bg="#F5F5F5")
    main.pack(fill="both", expand=True, padx=10, pady=10)
    
    config = tk.LabelFrame(main, text="⚙️ Configuração", font=("Arial", 12, "bold"), bg="white", padx=20, pady=20, relief="solid", bd=2)
    config.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    
    tk.Label(config, text="🎲 Tipo:", bg="white", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=8)
    tipos = [f"{k} números - {v['nome']}" for k, v in TIPOS_JOGOS.items()]
    combo_tipo = ttk.Combobox(config, values=tipos, state="readonly", width=32)
    combo_tipo.set(tipos[0])
    combo_tipo.grid(row=0, column=1, pady=8, sticky="ew")
    combo_tipo.bind("<<ComboboxSelected>>", atualizar_info_tipo)
    
    texto_info_jogo = tk.StringVar()
    tk.Label(config, textvariable=texto_info_jogo, bg="#F0F0F0", relief="solid", bd=1, padx=8, pady=5).grid(row=1, column=0, columnspan=2, pady=8, sticky="ew")
    atualizar_info_tipo()
    
    tk.Label(config, text="📊 Quantidade:", bg="white", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=8)
    entry_qtd = tk.Entry(config, font=("Arial", 11), width=15)
    entry_qtd.insert(0, "10")
    entry_qtd.grid(row=2, column=1, pady=8, sticky="w")
    
    tk.Label(config, text="🎯 Fixas:", bg="white", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=8)
    entry_fixas = tk.Entry(config, font=("Arial", 10))
    entry_fixas.grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")
    
    tk.Label(config, text="🚫 Descartadas:", bg="white", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky="w", pady=8)
    entry_descartadas = tk.Entry(config, font=("Arial", 10))
    entry_descartadas.grid(row=6, column=0, columnspan=2, pady=5, sticky="ew")
    
    botoes = tk.Frame(config, bg="white")
    botoes.grid(row=7, column=0, columnspan=2, pady=20)
    
    tk.Button(botoes, text="🔬 Análise ULTIMATE", command=buscar_analisar_ultimate, bg="#FF9800", fg="white", font=("Arial", 11, "bold"), padx=15, pady=12).pack(fill="x", pady=4)
    tk.Button(botoes, text="🎲 Gerar Jogos", command=gerar_jogos_ultimate, bg="#6A0DAD", fg="white", font=("Arial", 12, "bold"), padx=20, pady=14).pack(fill="x", pady=4)
    tk.Button(botoes, text="🗑️ Limpar", command=limpar, bg="#FF6B6B", fg="white", padx=20, pady=10).pack(fill="x", pady=4)
    tk.Button(botoes, text="📊 Excel", command=salvar_excel, bg="#4CAF50", fg="white", padx=20, pady=10).pack(fill="x", pady=4)
    tk.Button(botoes, text="📄 PDF", command=salvar_pdf, bg="#2196F3", fg="white", padx=20, pady=10).pack(fill="x", pady=4)
    
    preview = tk.LabelFrame(main, text="📋 Jogos", font=("Arial", 12, "bold"), bg="white", padx=20, pady=20, relief="solid", bd=2)
    preview.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
    
    text_preview = scrolledtext.ScrolledText(preview, font=("Courier", 8), bg="#FAFAFA", wrap="none")
    text_preview.pack(fill="both", expand=True)
    atualizar_preview()
    
    status = tk.Frame(main, bg="#1C1C1C", bd=2)
    status.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))
    
    texto_status = tk.StringVar()
    texto_status.set(f"✨ ULTIMATE v{VERSAO} pronto!")
    
    tk.Label(status, textvariable=texto_status, font=("Arial", 11, "bold"), bg="#1C1C1C", fg="#FFD700", padx=20, pady=10).pack(fill="x")
    
    main.columnconfigure(0, weight=1)
    main.columnconfigure(1, weight=3)
    main.rowconfigure(0, weight=1)
    
    root.mainloop()

if __name__ == "__main__":
    mostrar_splash()
    criar_interface()