import json
import os
import discord

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
  print("We are online and working.")

def load_status():
    try:
        with open("status.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

status = load_status()

def save_status(status):
    with open("status.json", "w") as file:
        json.dump(status, file, indent=4)

############################### Configurando o ambiente

# !!!Inserir USERNAME do usuário que pode alterar os registros!!!
admin = 'isabelleqga'
value = 'R$ 30,00'
method = '84998368093'

# Lista de nomes 'reais' que irão aparecer nas respostas
# Chaves no JSON
commands = {
    '!lp': "Luiz",
    '!chico': "Chico",
    '!ze': "Zé",
    '!caio': "Caio",
    '!thiago': "Thiago",
    '!pv': "PV",
    '!diego': "Diego",
    '!lipeira': "Lipeira",
    '!julia': "Júlia",
    '!marcal': "Marçal",
    '!wil': "Wil",
    '!rodrigo': "Rodrigo",
    '!isabelle': "Isabelle"
}

# (Opcional) Emojis dos pagantes, deixam as respostas mais interessantes
emojis = {
    "Luiz": "🏕️",
    "Chico": "💀",
    "Zé": "🏳️‍🌈",
    "Caio": "🧜‍♂️",
    "Thiago": "🐭",
    "PV": "🍫",
    "Diego": "🐡",
    "Lipeira": "🇧🇷",
    "Júlia": "🧚‍♀️",
    "Marçal": "🪩",
    "Wil": "🌬️",
    "Rodrigo": "🦁",
    "Isabelle": "🐝"
}

# Número do mês (digitado no comando) para nome
months = {
    '1': 'janeiro',
    '2': 'fevereiro',
    '3': 'março',
    '4': 'abril',
    '5': 'maio',
    '6': 'junho',
    '7': 'julho',
    '8': 'agosto',
    '9': 'setembro',
    '10': 'outubro',
    '11': 'novembro',
    '12': 'dezembro'
}

# Relacionando o comando ao nome da pessoa
def get_name(msg):
  for command in commands:
    if msg.startswith(command):
      return commands[command]

# Retorna o emoji usado pela pessoa
def get_emoji(name):
  return emojis.get(name, "🚩")

# Retorna nome do mês pelo número 
def get_month(msg):
  month_number = ''
  for char in reversed(msg): # Extrai o número do mês
      if char.isdigit():
          month_number = char + month_number
      else:
          break
  month = months.get(month_number, 'x') # Extrai o nome do mês
  return month 

# Retorna lista de nomes das pessoas que não pagaram em um mês específico
def get_unpaid_names(month):
    status = load_status()
    unpaid_names = [
        name for name, payments in status.items() if not payments.get(month, False)
    ]
    return unpaid_names

# Registra pagamento de uma pessoa em um mês específico
async def register_payment(message, nome, mes):
  # Verifica se o pagamento já foi registrado para este mês
  if status.get(nome.split()[0], {}).get(mes, False):
      await message.channel.send(
          f"👍 {nome} já pagou em {mes}! "
      )
  else:
    # Atualiza o status do pagamento no JSON
    status[nome.split()[0]][mes] = True 
    save_status(status)  
    
    # Envia uma mensagem confirmando o registro do pagamento
    await message.channel.send(
        f"👏 Boa, {nome}! Seu pagamento de **{mes}** foi registrado.\n\n"
    )
    # Lista os faltantes (se houver)
    await send_missing_payment_message(message, mes, get_unpaid_names(mes))

async def send_missing_payment_message(message, mes, faltantes):
  if len(faltantes) > 0:
      if len(faltantes) == 1:
          # Só uma pessoa não pagou 
          await message.channel.send(
              f"-----------------\n**👺📅 O caloterio de {mes} é:**\n\n" +
              "\n".join(
                  [f"- {name + ' ' + get_emoji(name)}"
                  for name in faltantes]) +
              "\n\n 💵 *Valor: "+value+"*\n📲 *Pix: "+method+"*\n-----------------"
          )
      else:
          # Mais de uma pessoa não pagou
          await message.channel.send(
              f"-----------------\n**👺📅 Faltantes de {mes}:**\n\n" + "\n".join(
                  [f"- {name + ' ' + get_emoji(name)}"
                  for name in faltantes]) +
              "\n\n 💵 *Valor: "+value+"*\n📲 *Pix: "+method+"*\n-----------------"
          )
      await message.channel.send(
          f"💰 **Temos R$ {30*sum(1 for payments in status.values() for payment in payments.values() if payment)},00 na Caixinha.**"
      )
  else:
      # Mensagem de todos os pagamentos do mês feitos
      await message.channel.send(
          f"-----------------\n🎉 Parabéns, galera! Todos os pagamentos de **{mes}** foram feitos! \n\n💰 **Atualmente temos R$ {30*sum(1 for payments in status.values() for payment in payments.values() if payment)},00 na Caixinha.**\n----------------- \n👋 Até a próxima!"
      )


@client.event
# Ouvindo todas as mensagens que são enviadas no canal
async def on_message(message):
  msg = message.content
  
  # Caso o autor seja ele mesmo (o bot): Ignora a mensagem
  if message.author == client.user:
      return
  # Caso o autor seja a pessoa responsável pelos registros 
  elif message.author.name == admin:
      if any(command in msg for command in commands):
          # Transforma o número do mês em nome (usados nas mensagens e no JSON)
          mes = get_month(msg) 
          if mes != "x": #Verifica se digitou um mês
              nome = get_name(msg)
              if nome: #Verifica se o nome é reconhecido 
                # Registra o pagamento
                await register_payment(message, nome, mes)
              else: 
                await message.channel.send("🤔 Quem?!")
          else:
              await message.channel.send("📅 Lembre-se do mês do pagamento!")
      elif msg.startswith("!status"):
          mes = get_month(msg) 
          if mes != "x": #Verifica se digitou um mês
              await send_missing_payment_message(message, mes, get_unpaid_names(mes))
          else:
              await message.channel.send("📅 Lembre-se do mês do pagamento!")
      else:
          await message.channel.send("🤔 Não entendi...")
  # Caso o autor seja um usuário qualquer: Bot não obedece
  else:
      await message.channel.send("😎 Tu não manda em mim, rapaz!")

client.run(os.environ['TOKEN'])
