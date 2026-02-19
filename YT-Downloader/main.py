from pytubefix import YouTube
from pprint import pprint
from tkinter import Tk
from tkinter.filedialog import askdirectory
from pathvalidate import sanitize_filename, sanitize_filepath
from moviepy import *
import time, os

tk = Tk()
tk.withdraw()

def clear():
  os.system("cls")

def psay(thing):
  pprint(thing)

step = 0

# Example:
# [{
#   "itag":123,
#   "url": "http://...",
#   "title":"Never Gonna Give You Up",
#   "file_type":"audio ou video",
#   "size_mb":1.23,
#   "duration":"1:00:00",
#   PARA ÁUDIO
#   "audio_quality":"160kbps" (abr)
#
#   PARA VÍDEO:
#   "resolução": 1234x123
#   "res":"1080p",
#   "fps":"25fps"
# }]
queue = []
download_path = str("./")

# Shows selected items for download
def list_queue():
  print("Fila de download:")
  for idx, item in enumerate(queue):
    print(f"[{idx+1}] {item['title']}")

# Gets new download path
def set_download_path():
  return str(askdirectory())

#sair = False
def menu():
  global download_path, queue
  while True:
    #clear()
    choice = ""
    #choice = 2
    print(
      "Selecione uma opção:\n",
      "1- Adicionar Vídeo / Música;\n",
      "2- Ver fila de Download;\n",
      "3- Remover item da fila;\n",
      "4- Mudar ordem da fila;\n", # Adicionar modo de "Editar item na fila"
      "5- Pasta de Download;\n",
      "6- Baixar seleções;\n"
    )
    #print(download_path) download path debug
    while type(choice) == str:
      try:
        choice = int(input("Digite: "))
      except ValueError: pass
    print("-----------------")

    match choice:
      case 1:
        #url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        url = str(input("Digite a URL do vídeo: "))
        download_sequence(url)

      case 2: # Fila de download;
        clear()
        list_queue()
        input("Aperte ENTER para voltar ao menu.")
      
      case 3: # Remover item da fila;
        clear()
        idx_to_remove = -1
        while idx_to_remove < 0 or idx_to_remove > len(queue) + 1:
          clear()
          print("[0] LIMPAR LISTA")
          list_queue()
          try:
            idx_to_remove = int(input("Digite o número do item a ser removido: "))
          except ValueError: pass
        
        clear()
        if idx_to_remove == 0:
          queue = []
          print("Lista esvaziada.")
        else:
          queue.pop(idx_to_remove-1)
          print("Item removido, lista atualizada:")
          list_queue()
        
        input("Aperte ENTER para voltar ao menu.")

      case 4: # Trocar ordem;
        item1, item2 = 0, 0
        while item1 <= 0 or item1 > len(queue) + 1 or item1 == "":
          try:
            list_queue()
            item1 = int(input("Item 1: "))
          except (ValueError, TypeError): pass
        while item2 <= 0 or item2 > len(queue) + 1 or item2 == "":
          try:
            list_queue()
            item2 = int(input("Item 2: "))
          except (ValueError, TypeError): pass

        if item1 != item2:
          queue[item1-1], queue[item2-1] = queue[item2-1], queue[item1-1]
          clear()
          print("Itens alternados, lista atualizada:")
          list_queue()
          input("Aperte ENTER para voltar ao menu.")
        else:
          clear()
          print("Houve um erro, tente novamente.")
          input("Aperte ENTER para voltar ao menu.")
      
      case 5:
        download_path = set_download_path()
        print(
          "Caminho de download atualizado para:\n",
          f"{download_path}"
        )
        input("Aperte ENTER para voltar ao menu.")
      
      case 6:
        for idx, item in enumerate(queue):
          download(item)
          print(f"[{idx + 1}] {item['title']} | Baixado")
        
        input("Downloads finalizados, aperte ENTER para voltar ao menu.")
        clear()

# Remove an item
def remove_choice(position):
  queue.pop(position-1)

# Switch download order between items
def switch_positions(first_pos, second_pos):
  first_item, second_item = queue[first_pos-1], queue[second_pos-1]
  queue[first_pos-1], queue[second_pos-1] = second_item, first_item

def get_file_type():
  file_type = ""
  while str(file_type).strip() == "" or type(file_type) != int:
    clear()
    print(
      "Qual o tipo de arquivo?\n",
      "1- Áudio;\n",
      "2- Vídeo;\n",
      "3- Cancelar;"
    )
    try:
      file_type = int(input("Digite: "))
    except (ValueError, TypeError): pass
  
  match file_type:
    case 1: file_type = "audio"
    case 2: file_type = "video"
    case 3: file_type = False

  print("--------------------------------------------------------------------------------------")
  return file_type

# Returns download options
def search_streams(url, file_type):
  if file_type == "audio":
    return [YouTube(url).streams.filter(type=file_type), YouTube(url).title]
  else:
    return [YouTube(url).streams.filter(type=file_type, mime_type="video/mp4", adaptive=True), YouTube(url).title]

def create_object(item, chosen_type, url):

  def format_duration(durationMS):
    durationMS = int(durationMS)
    seconds = round((durationMS//1000)%60)
    minutes = int(durationMS/1000//60)
    hours = int(minutes//60)
    return f"{hours:02d}:{minutes:02d}:{seconds:.02f}"
  duration = format_duration(item["durationMs"])

  itag = item["itag"]
  #file_type = item["subtype"]
  file_type = item["type"]
  size = item["_filesize_mb"]
  stream_data = {"itag":itag,
            "url":url,
            "file_type":file_type,
            "size":size,
            "duration":duration}
  if chosen_type == "audio":
    stream_data["abr"] = item["abr"]
    stream_data["duration"]
  else:
    #print(stream_data)
    stream_data["resolução"] = f"{item['_width']}x{item['_height']}"
    stream_data["res"] = item["resolution"]
    stream_data["fps"] = item["fps"]
  
  return stream_data

def get_download_options(url, file_type):
  raw_streams, title = search_streams(url, file_type)
  # print(raw_streams) # Debug
  available_choices = []
  for item in raw_streams:
    item = vars(item)
    #print(item)
    option = create_object(item, file_type, url)
    option["title"] = title
    option["url"] = url
    available_choices.append(option)
  
  return (available_choices, title)

def display_download_options(options, file_type):
  available_choices, title = options
  print(f"Opções para download de:\n {title}")
  print("[0] Cancelar seleção e voltar ao menu.")
  for num, item in enumerate(available_choices):
    if file_type == "audio":
      print(f"[{num+1}] ITAG: {item['itag']} | Duração: {item['duration']} | Qualidade: {item['abr']} | Tamanho (MB): {item['size']}")
    else:
      print(f"[{num+1}] ITAG: {item['itag']} | Duração: {item['duration']} | Qualidade: {item['res']} | Tamanho (MB): {item['size']} | Resolução: {item['resolução']} | FPS: {item['fps']}")

def download(item):
  file_type = item["file_type"]
  #print(item) # Debug
  if file_type == "audio": # Just Audio
    YouTube(item["url"]).streams.get_by_itag(item["itag"]).download(output_path=download_path, filename=f"{item['title']}.mp3")
  else: # Video + Audio
    # Downloads Video
    YouTube(item["url"]).streams.get_by_itag(item["itag"]).download(filename="temp_video.mp4", output_path=download_path)

    # Downloads Audio
    if file_type != "audio":
      audio_itag = vars(YouTube(item["url"]).streams.filter(type="audio", abr="128kbps")[0])["itag"]
      if not audio_itag:
        print("Maior qualidade")
        audio_itag = vars(YouTube(item["url"]).streams.filter(type="audio").order_by(attribute_name="abr")[-1])["itag"]

    YouTube(item["url"]).streams.get_by_itag(str(audio_itag)).download(filename="temp_audio.mp3", output_path=download_path)

    # Video + Audio
    video_path = sanitize_filepath(f"{download_path}/temp_video.mp4")
    audio_path = sanitize_filepath(f"{download_path}/temp_audio.mp3")

    temp_video = VideoFileClip(video_path)
    temp_audio = AudioFileClip(audio_path)

    final_video = temp_video.with_audio(temp_audio)

    unclear_title = item["title"]
    new_title = sanitize_filename(unclear_title)

    final_video.write_videofile(sanitize_filepath(f"{download_path}/{new_title}.mp4"))

    # Deleting temp files
    def delete_files(path):
      os.remove(path)

    time.sleep(3)
    delete_files(video_path)
    delete_files(audio_path)
# Main Scripts
def download_sequence(url):
  file_type = get_file_type()
  if not file_type: return False

  clear()
  escolha_item = -1
  options_and_title = get_download_options(url, file_type)
  itens, title = options_and_title[0], options_and_title[1]
  while escolha_item < 0 or escolha_item > len(itens):
    display_download_options(options_and_title, file_type)
    try:
      escolha_item = int(input("Sua escolha: "))
    except (ValueError, TypeError): pass

  if escolha_item == 0:
    clear()
    input("Escolha cancelada, aperte ENTER para retornar ao menu.")
    return
  
  queue.append(itens[escolha_item-1])
  custom_title = str(input("Escreva um nome para o arquivo ou deixe em branco para usar o título do vídeo: ")).strip()
  if custom_title:
    queue[-1]["title"] = custom_title
  print(
    "Item adicionado à lista de Download:\n",
    queue[-1]["title"]
  )
  input("Aperte ENTER para voltar ao menu.")
  clear()

menu()
#download_sequence("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
