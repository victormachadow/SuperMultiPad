import os
import tkinter as tk
from tkinter import scrolledtext
import re
#v7

def listar_arquivos(diretorio):
    arquivos = [f for f in os.listdir(diretorio) if f.endswith('.txt') and os.path.isfile(os.path.join(diretorio, f))]
    return arquivos

def exibir_arquivos(event):
    print(diretorio_atual.get())
    selected_item = listbox.curselection()
    if selected_item:
        indice = selected_item[0]
        nome_item = listbox.get(indice)
        caminho_item = os.path.join(diretorio_atual.get(), nome_item)
        diretorio_selecionado.set(caminho_item)
        if not caminho_item.endswith('.txt'):
         atualizar_lista_arquivos()
        if caminho_item.endswith('.py'): #Arquivos terminados em py 
          print("arquivo python")
        if caminho_item.endswith('.txt'): #Arquivos terminados em txt
         with open(caminho_item, 'r') as arquivo:
            conteudo = arquivo.read()
            #conteudo_formatado = formatar_conteudo(conteudo)
            #atualizar_textbox(conteudo_formatado)
            atualizar_textbox(conteudo)
            listbox_arquivos.delete(0, tk.END) #Apaga lista de arquivos para não confundir usuários
            

def atualizar_lista_arquivos():
    arquivos = listar_arquivos(diretorio_selecionado.get())
    listbox_arquivos.delete(0, tk.END)
    for arquivo in arquivos:
        listbox_arquivos.insert(tk.END, arquivo)

def exibir_conteudo_arquivo(event):
    selected_item = listbox_arquivos.curselection()
    if selected_item:
        indice = selected_item[0]
        nome_arquivo = listbox_arquivos.get(indice)
        caminho_arquivo = os.path.join(diretorio_selecionado.get(), nome_arquivo)
        if not nome_arquivo.endswith('.txt'): 
         print("não é texto")
        with open(caminho_arquivo, 'r') as arquivo:
            conteudo = arquivo.read()
            atualizar_textbox(conteudo)

def atualizar_textbox(conteudo):
    textbox.delete('1.0', tk.END)
    textbox.insert(tk.END, conteudo)
    formatar_links()
    formatar_negrito()
    formatar_italico()
    
def formatar_links():
    content = textbox.get("1.0", tk.END)
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
    for url in urls:
        start = textbox.search(url, "1.0", tk.END)
        end = f"{start}+{len(url)}c"
        textbox.tag_add("link", start, end)
        textbox.tag_config("link", foreground="blue", underline=True)
        textbox.tag_bind("link", "<Enter>", on_enter)
        textbox.tag_bind("link", "<Leave>", on_leave)
        textbox.tag_bind("link", "<Button-1>", lambda event, url=url: on_click(url))
        
        
def formatar_negrito():
    content = textbox.get("1.0", tk.END)
    bold_words = re.findall(r'#\w+', content)
    for word in bold_words:
        start = textbox.search(word, "1.0", tk.END)
        end = f"{start}+{len(word)}c"
        textbox.tag_add("negrito", start, end)
        textbox.tag_config("negrito", font=("Helvetica", 12, "bold"))

def formatar_italico():
    content = textbox.get("1.0", tk.END)
    italic_words = re.findall(r'\*\w+', content)
    for word in italic_words:
        start = textbox.search(word, "1.0", tk.END)
        end = f"{start}+{len(word)}c"
        textbox.tag_add("italico", start, end)
        textbox.tag_config("italico", font=("Helvetica", 12, "italic"))        

def on_enter(event):
    textbox.config(cursor="hand2")

def on_leave(event):
    textbox.config(cursor="")

def on_click(url):
    os.system(f"start {url}")  # Abrir URL no navegador    
    

def formatar_conteudo(conteudo): #Deprecated
    def link_replacer(match):
        url = match.group()
        return f'<a href="{url}">{url}</a>'
    
    # Expressão regular para detectar URLs
    url_pattern = r'(https?://\S+)'
    
    conteudo_formatado = re.sub(url_pattern, link_replacer, conteudo)
    return conteudo_formatado
    
    
def salvar_arquivo():
    caminho_arquivo = diretorio_selecionado.get()
    if caminho_arquivo and caminho_arquivo.endswith('.txt'):
        conteudo = textbox.get("1.0", tk.END)
        with open(caminho_arquivo, 'w') as arquivo:
            arquivo.write(conteudo)



root = tk.Tk()
root.title("Exibição de Diretórios e Arquivos .txt")

diretorio_atual = tk.StringVar(value=os.getcwd())
diretorio_selecionado = tk.StringVar()

listbox = tk.Listbox(root)
itens = os.listdir(diretorio_atual.get())
for item in itens:
    listbox.insert(tk.END, item)
listbox.grid(row=0, column=0, padx=10, pady=10, sticky='ns')

listbox_arquivos = tk.Listbox(root)
listbox_arquivos.grid(row=0, column=1, padx=10, pady=10, sticky='ns')

textbox = scrolledtext.ScrolledText(root, wrap=tk.WORD)
textbox.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')

listbox.bind("<<ListboxSelect>>", exibir_arquivos)
listbox_arquivos.bind("<<ListboxSelect>>", exibir_conteudo_arquivo)

root.grid_columnconfigure(2, weight=1)
root.grid_rowconfigure(0, weight=1)

salvar_button = tk.Button(root, text="Salvar", command=salvar_arquivo)
salvar_button.grid(row=1, column=1, padx=10, pady=10)


root.mainloop()
