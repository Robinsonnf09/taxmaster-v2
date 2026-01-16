# No código atual, linha ~734, função buscar_analisar_ultimate()
# ADICIONE este código para mostrar progresso na interface:

def buscar_analisar_ultimate():
    """Análise ultimate com progresso visual"""
    
    # Criar janela de progresso
    janela_prog = tk.Toplevel(root)
    janela_prog.title("⏳ Carregando Análise ULTIMATE")
    janela_prog.geometry("500x200")
    janela_prog.transient(root)
    janela_prog.grab_set()
    
    tk.Label(janela_prog, text="📥 Baixando Histórico...", font=("Arial", 14, "bold")).pack(pady=20)
    
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(janela_prog, length=400, mode='determinate', variable=progress_var)
    progress_bar.pack(pady=10)
    
    label_prog = tk.Label(janela_prog, text="Iniciando...", font=("Arial", 10))
    label_prog.pack(pady=10)
    
    def task():
        try:
            # Código de carregamento com atualização de progresso
            # ... (resto do código)
            
            janela_prog.destroy()
            # Abrir dashboard
            
        except Exception as e:
            janela_prog.destroy()
            messagebox.showerror("Erro", str(e))
    
    thread = threading.Thread(target=task, daemon=True)
    thread.start()