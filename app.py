import os
import tkinter as tk
from tkinter import scrolledtext
import re
import subprocess
import struct
#import pylnk
#v7

link_tags = {}

def resolve_atalho(atalho):
    try:
        with open(atalho, 'rb') as f:
            # Lê o arquivo .lnk e analisa seu conteúdo
            content = f.read()
            
            # Verifica se o arquivo .lnk começa com a assinatura 'L' 'K' ' '. 'f' (0x4C 0x00 0x4B 0x00 0x20 0x00 0x00 0x00)
            if content[:8] != b'\x4C\x00\x4B\x00\x20\x00\x00\x00':
                raise ValueError("O arquivo não é um atalho válido (.lnk).")

            # Pula os primeiros 20 bytes
            shell_items_offset = struct.unpack('<I', content[0x14:0x18])[0]
            shell_items = content[shell_items_offset:]

            # Encontra o ponto de início do caminho alvo
            start = shell_items.find(b'\x00\x00\x00')
            if start == -1:
                raise ValueError("Não foi possível encontrar o caminho alvo no atalho.")
            
            # Pula os bytes nulos
            start += 4
            
            # Lê o caminho alvo como uma sequência de caracteres de 2 bytes (UTF-16 little-endian)
            target_path = shell_items[start:].decode('utf-16le')
            return target_path
    except Exception as e:
        print(f"Erro ao resolver o atalho: {e}")
        return None

def listar_arquivos(diretorio):
    arquivos = [f for f in os.listdir(diretorio) if f.endswith('.txt') or f.endswith('.py') or f.endswith('.lnk') and os.path.isfile(os.path.join(diretorio, f))]
    return arquivos

def exibir_arquivos(event): #Aqui abre os diretorios e atualiza os arquivos ou abre os arquivos na pasta raiz
    print(diretorio_atual.get())
    selected_item = listbox.curselection()
    if selected_item:
        indice = selected_item[0]
        nome_item = listbox.get(indice)
        caminho_item = os.path.join(diretorio_atual.get(), nome_item)
        diretorio_selecionado.set(caminho_item)
        if not caminho_item.endswith('.txt'):
          if caminho_item.endswith('.py'):
            print("arquivo python")
          if caminho_item.endswith('.lnk'):
            pass
            #resolve_atalho(caminho_item)
            
          atualizar_lista_arquivos()
        if caminho_item.endswith('.txt'): #Arquivos terminados em txt
         with open(caminho_item, 'r') as arquivo:
            conteudo = arquivo.read()
            #conteudo_formatado = formatar_conteudo(conteudo)
            #atualizar_textbox(conteudo_formatado)
            atualizar_textbox(conteudo)
            listbox_arquivos.delete(0, tk.END) #Apaga lista de arquivos para não confundir usuários
        #Implementar chamada de arquivos .py e .exe    

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
        if not caminho_arquivo.endswith('.txt'):
         if caminho_arquivo.endswith('.py'):
          print("arquivo py")
         if caminho_arquivo.endswith('.exe'):
          print("arquivo exe")
         if caminho_arquivo.endswith('.lnk'):
          pass
          #resolve_atalho(caminho_arquivo)
        if caminho_arquivo.endswith('.txt'): 
         with open(caminho_arquivo, 'r') as arquivo:
            conteudo = arquivo.read()
            atualizar_textbox(conteudo)

def atualizar_textbox(conteudo):
    textbox.delete('1.0', tk.END)
    textbox.insert(tk.END, conteudo)
    formatar_links()
    formatar_negrito()
    formatar_italico()
    
def formatar_linksDeprecated(): #Os links não estão sendo reconhecidos de forma correta tanto no diretorio raiz quanto nos subs
    content = textbox.get("1.0", tk.END)
    
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
    for url in urls:
       
        print("Urls :"+url)
        start = textbox.search(url, "1.0", tk.END)
        end = f"{start}+{len(url)}c"
        textbox.tag_add("link", start, end)
        textbox.tag_config("link", foreground="blue", underline=True) 
        textbox.tag_bind("link", "<Enter>", on_enter)
        textbox.tag_bind("link", "<Leave>", on_leave)
        textbox.tag_bind("link", "<Button-1>", lambda event, url=url: on_click(url))
     
        
        
def formatar_links():
    content = textbox.get("1.0", tk.END)
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
    
    for index, url in enumerate(urls):
        start = textbox.search(url, "1.0", tk.END)
        end = f"{start}+{len(url)}c"
        # Crie um nome exclusivo para a tag usando o índice
        tag_name = f"link_{index}"
        textbox.tag_add(tag_name, start, end)
        textbox.tag_config(tag_name, foreground="blue", underline=True)
        
        # Associe uma função de callback que captura a URL atual
        def on_link_click(event, current_url=url):
            on_click(current_url)
        
        textbox.tag_bind(tag_name, "<Button-1>", on_link_click)
       
        
        
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
    print("Url é :"+url)
    #Rei do Consignado : Profile 4
    #Dino Rifas : Profile 2
    nome_perfil = "Profile 4"
    #os.system(f"start {url}")  # Abrir URL no navegador
    os.system(f'start chrome --profile-directory="{nome_perfil}" "{url}"')
    
def on_link_click(event):
    tag = event.widget.tag_names(tk.CURRENT)  # Obtem as tags aplicadas ao texto clicado
    print(tag)
    

    
    
def salvar_arquivo(): #Não salva arquivo em subdiretorio
    caminho_arquivo = diretorio_selecionado.get()
    if caminho_arquivo and caminho_arquivo.endswith('.txt'):
        conteudo = textbox.get("1.0", tk.END)
        with open(caminho_arquivo, 'w') as arquivo:
            arquivo.write(conteudo)

def buscar_texto(): #Só está pegando a primeira linha do arquivo
    # Limpe os destaques anteriores
    textbox.tag_remove("encontrado", "1.0", tk.END)
    texto_pesquisa = search_entry.get()
    conteudo_texto = textbox.get("1.0", tk.END)
    texto_pesquisa = search_entry.get()  # Obtenha o texto da caixa de pesquisa
    conteudo_texto = textbox.get("1.0", tk.END)  # Obtenha o conteúdo do texto exibido
    if texto_pesquisa:
        # Realize a busca no conteúdo do texto
        inicio = conteudo_texto.find(texto_pesquisa)
        if inicio != -1:
            fim = inicio + len(texto_pesquisa)
            # Destaque o texto encontrado
            textbox.tag_add("encontrado", f"1.{inicio}", f"1.{fim}")
            textbox.tag_config("encontrado", background="yellow", foreground="black")
        else:
            print("Texto não encontrado.")


root = tk.Tk()
print("Projeto: "+os.path.basename(os.getcwd()))
titulo = os.path.basename(os.getcwd())
root.title(titulo)

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

search_entry = tk.Entry(root) #Campo entrada busca
search_entry.grid(row=1, column=2, padx=10, pady=10)

search_button = tk.Button(root, text="Buscar", command=buscar_texto) #Botao de pesquisar
search_button.grid(row=1, column=3, padx=10, pady=10)

#formatar_button = tk.Button(root, text="Format", command=formatar_links) #Botao de pesquisar
#formatar_button.grid(row=1, column=4, padx=10, pady=10)


root.mainloop()
