import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import ttkbootstrap as tb

# Caminho da pasta onde estão os arquivos XMLs
directory = r"\\10.0.0.225\Xmls\sincronizadas"
log_path = os.path.join(os.path.expanduser("~"), "Desktop", f"LOG_EXCLUSAO_{datetime.datetime.now().strftime('%d-%m-%Y')}.txt")
cutoff_date = datetime.datetime(2023, 12, 31)  # Data limite para exclusão
running = False  # Flag para verificar se o processo está em andamento

# Função para exibir o emoji do astronauta e eventualmente a mensagem
def show_astronauta():
    astronaut_label = tk.Label(frame, text="👨‍🚀", font=("Helvetica", 50), bg="white")
    astronaut_label.place(relx=1.0, rely=1.0, anchor="se")  # Posicionando no canto inferior direito

    # Função para mostrar a frase "Olhe para sua cadeira, é um aviso"
    def show_message():
        if running:
            # Exibe a mensagem a cada 30 segundos
            message_label = tk.Label(frame, text="Olhe para sua cadeira, é um aviso", font=("Helvetica", 12, "bold"), fg="white", bg="green")
            message_label.place(relx=1.0, rely=0.9, anchor="se")  # Coloca a mensagem logo acima do astronauta
            frame.after(3000, message_label.destroy)  # Remove a mensagem após 3 segundos
            frame.after(30000, show_message)  # Repete a mensagem a cada 30 segundos

    show_message()

# Função para excluir arquivos XML antigos
def delete_old_xmls():
    global running
    running = True
    total_deleted = 0
    total_files = 0  # Contador de arquivos encontrados
    deleted_files = []
    
    status_label.config(text="Buscando e excluindo arquivos...")
    root.update_idletasks()

    # Função que realiza a exclusão de arquivos XML
    def worker(root_dir, files):
        nonlocal total_deleted, total_files
        for file_path in files:
            if not running:
                break
            try:
                modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                if modified_time <= cutoff_date:
                    os.remove(file_path)
                    deleted_files.append(file_path)
                    total_deleted += 1
                total_files += 1
                update_ui(total_deleted, total_files)  # Atualiza a interface com o número de arquivos excluídos e encontrados
                
            except Exception as e:
                print(f"Erro ao excluir {file_path}: {e}")

    # Percorrendo as pastas e arquivos
    for root_dir, _, files in os.walk(directory):
        if not running:
            break
        xml_files = [os.path.join(root_dir, file) for file in files if file.lower().endswith(".xml")]
        worker(root_dir, xml_files)

    # Salvando log de exclusão
    with open(log_path, "w") as log:
        log.write("Arquivos excluídos:\n" + "\n".join(deleted_files) + f"\nTotal: {total_deleted} arquivos.")
    
    # Exibindo mensagem de conclusão
    messagebox.showinfo("Conclusão", f"Processo concluído! {total_deleted} arquivos excluídos.")
    progress_bar.stop()

# Função para atualizar a interface
def update_ui(count_deleted, count_found):
    progress_bar.step(1)  # Atualiza a barra de progresso
    status_label.config(text=f"Arquivos encontrados: {count_found}, Excluídos: {count_deleted}")
    root.update_idletasks()

# Função para iniciar o processo
def start_process():
    global running
    if not running:
        progress_bar.start(10)  # Inicia a barra de progresso
        threading.Thread(target=delete_old_xmls, daemon=True).start()  # Inicia o processo de exclusão em outra thread

# Função para parar o processo
def stop_process():
    global running
    running = False  # Para o processo
    messagebox.showinfo("Pausado", "O processo foi pausado.")
    progress_bar.stop()  # Para a barra de progresso

# UI Setup
root = tb.Window(themename="superhero")  # Usando o tema 'superhero' do ttkbootstrap
root.title("Exclusão de XMLs")
root.geometry("500x500")

frame = ttk.Frame(root, padding=20)
frame.pack(expand=True, fill="both")  # Garantir que o frame preencha toda a área

# Título da interface
title_label = ttk.Label(frame, text="Exclusão de XMLs", font=("Helvetica", 16, "bold"))
title_label.pack()

# Status da exclusão
status_label = ttk.Label(frame, text="Aguardando início...", font=("Helvetica", 12))
status_label.pack(pady=10)

# Barra de progresso
progress_bar = ttk.Progressbar(frame, orient="horizontal", mode="determinate", length=300)
progress_bar.pack(pady=10)

# Botões de iniciar e parar
button_frame = ttk.Frame(frame)
start_btn = tb.Button(button_frame, text="Iniciar", bootstyle="success", command=start_process)
start_btn.pack(side="left", padx=10)
stop_btn = tb.Button(button_frame, text="Parar", bootstyle="danger", command=stop_process)
stop_btn.pack(side="right", padx=10)
button_frame.pack(pady=20)

# Exibindo o astronauta e a mensagem
show_astronauta()

root.mainloop()
