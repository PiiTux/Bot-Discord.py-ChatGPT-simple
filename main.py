# Importation des modules nécessaires
from os import getenv
from dotenv import load_dotenv
from discord import Activity, ActivityType, Client, Intents
from openai import OpenAI

# Instructions pour l'assistant
PROMPT = "Tu es un assistant utile. Tes réponses sont toujours courtes avec des émojis."
# Modèle à utiliser
MODEL = "gpt-3.5-turbo"
# Liste des ID des salons où le bot doit répondre
CHANNELS = (0000000000000000000, 0000000000000000000)
# Nom et du type d'activité du bot
ACTIVITY_NAME = "répondre aux questions"
ACTIVITY_TYPE = ActivityType.playing
# Longueur de l'historique des messages
HISTORY_LENGTH = 9

# Chargement des variables d'environnement à partir du fichier .env
load_dotenv()

# Création de l'activité
activity = Activity(name=ACTIVITY_NAME, type=ACTIVITY_TYPE)
intents = Intents.default()
intents.message_content = True

# Récupération du jeton d'accès Discord à partir des variables d'environnement
TOKEN = getenv("DISCORD_TOKEN")

# Création du client Discord et de l'instance OpenAI
client = Client(activity=activity, intents=intents)
openai = OpenAI()


# Événement déclenché lorsque le bot est prêt
@client.event
async def on_ready():
    print(f"Prêt ! Connecté en tant que {client.user}")


# Événement déclenché lorsqu'un message est envoyé
@client.event
async def on_message(message):
    # Vérification que le message n'est pas envoyé par un bot et qu'il n'est pas vide
    if message.author.bot or not message.content:
        return
    # Vérification que le bot est mentionné dans le message ou que le message est envoyé dans un salon autorisé
    if client.user not in message.mentions and message.channel.id not in CHANNELS:
        return

    # Création de la liste des messages
    messages = [
        {
            "role": "system",
            "content": PROMPT,
        }
    ]

    # Envoi d'une indication que le bot est en train d'écrire
    async with message.channel.typing():
    # Récupération de l'historique des messages du salon
        async for msg in message.channel.history(limit=HISTORY_LENGTH):
            # Si le message a été envoyé par un autre bot ou est vide, on passe au suivant
            if (msg.author.bot and msg.author != client.user) or not msg.content:
                continue

            # Ajout du message et de son rôle à la liste des messages
            messages.append(
                {
                    "role": "assistant" if msg.author.bot else "user",
                    "content": msg.content,
                    "name": str(msg.author.id)
                }
            )

        # Inversion de l'ordre des messages
        messages.reverse()

        # Appel à l'API OpenAI pour générer une réponse
        completion = openai.chat.completions.create(
            model=MODEL,
            messages=messages,
        )

        # Envoi de la réponse générée par ChatGPT
        await message.reply(completion.choices[0].message.content)


# Démarrage du client Discord avec le jeton d'accès
client.run(TOKEN)
