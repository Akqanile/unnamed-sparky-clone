import discord
from discord.ext import commands
import asyncio
import random
import json
import os
 
with open('levels.json') as f:
    levels: dict = json.load(f)

with open('config.json') as f:
    config: dict = json.load(f)

intents: discord.Intents = discord.Intents.default()
intents.message_content = True

bot: discord.Client = commands.Bot(command_prefix = config['prefix'], intents = intents)

active_guesses: list[int] = []

DIFFICULTIES = ['easy', 'medium', 'hard']

@commands.command(name='guess', aliases=['g'])
async def guess(ctx: commands.context.Context, difficulty: str = None):
    if ctx.channel.id in active_guesses:
        return await ctx.reply(embed = discord.Embed(title = "There's already a game going on in this channel!"), mention_author = False)
    
    active_guesses.append(ctx.channel.id)

    if difficulty is None or difficulty.lower() not in DIFFICULTIES:
        difficulty = random.choices(DIFFICULTIES + ['legendary'], [0.3, 0.20, 0.39, 0.01])[0]
    
    match difficulty:
        case 'legendary':
            embed_colour = 0xff9bfc
        case 'easy':
            embed_colour = 0x8bd66b
        case 'medium':
            embed_colour = 0xf49d46
        case 'hard':
            embed_colour = 0xd64228

    level: dict = levels[difficulty][random.randint(0, len(levels[difficulty]) - 1)]

    embed: discord.Embed = discord.Embed(title = 'Guess the level!', description = f'Difficulty: {difficulty.capitalize()}', colour = embed_colour)
    
    footer: dict = {'text': f'Requested by {ctx.author.name}#{ctx.author.discriminator}'}

    avatar = ctx.author.avatar

    if avatar is not None:
        footer['icon_url'] = avatar.url
    
    embed.set_footer(**footer)

    if level['image'].startswith('/'):
        # https://stackoverflow.com/a/61579108
        file: discord.File = discord.File(f"{os.getcwd()}{level['image']}", filename = 'image.png')
        embed.set_image(url = 'attachment://image.png')
        question: discord.Message = await ctx.send(file = file, embed = embed)
    else:
        embed.set_image(url = level['image'])
        question: discord.Message = await ctx.send(embed = embed)
    
    def answer_is_correct(message: discord.Message) -> bool:
        return message.content.lower() == level['name'].lower()
    
    try:
        answer: discord.Message = await bot.wait_for('message', timeout = 15, check = answer_is_correct)
        await answer.reply(embed = discord.Embed(title = f"Congratulations! You guessed {level['name']} correctly!", colour = embed_colour))
    except asyncio.TimeoutError:
        await question.reply(embed = discord.Embed(title = "Time's up!"))

    active_guesses.remove(ctx.channel.id)

bot.add_command(guess)

if __name__ == '__main__':
    bot.run(config['token'])