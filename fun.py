
import random
import requests
import html
import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import Context
from datetime import datetime
import asyncio

class Choice(discord.ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.value = None


    @discord.ui.button(label="Heads", style=discord.ButtonStyle.blurple)
    async def confirm(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        self.value = "heads"
        self.stop()

    @discord.ui.button(label="Tails", style=discord.ButtonStyle.blurple)
    async def cancel(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        self.value = "tails"
        self.stop()


class RockPaperScissors(discord.ui.Select):
    def __init__(self) -> None:
        options = [
            discord.SelectOption(
                label="Scissors", description="You choose scissors.", emoji="✂"
            ),
            discord.SelectOption(
                label="Rock", description="You choose rock.", emoji="🪨"
            ),
            discord.SelectOption(
                label="Paper", description="You choose paper.", emoji="🧻"
            ),
        ]
        super().__init__(
            placeholder="Choose...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        choices = {
            "rock": 0,
            "paper": 1,
            "scissors": 2,
        }
        user_choice = self.values[0].lower()
        user_choice_index = choices[user_choice]

        bot_choice = random.choice(list(choices.keys()))
        bot_choice_index = choices[bot_choice]

        result_embed = discord.Embed(color=0xBEBEFE)
        result_embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.display_avatar.url
        )

        winner = (3 + user_choice_index - bot_choice_index) % 3
        if winner == 0:
            result_embed.description = f"**That's a draw!**\nYou've chosen {user_choice} and I've chosen {bot_choice}."
            result_embed.colour = 0xF59E42
        elif winner == 1:
            result_embed.description = f"**You won!**\nYou've chosen {user_choice} and I've chosen {bot_choice}."
            result_embed.colour = 0x57F287
        else:
            result_embed.description = f"**You lost!**\nYou've chosen {user_choice} and I've chosen {bot_choice}."
            result_embed.colour = 0xE02B2B

        await interaction.response.edit_message(
            embed=result_embed, content=None, view=None
        )


class RockPaperScissorsView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.add_item(RockPaperScissors())

class TriviaButton(discord.ui.Button):
    def __init__(self, label, answer, correct_answer, **kwargs):
        super().__init__(label=label, **kwargs)
        self.answer = answer
        self.correct_answer = correct_answer

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.answer == self.correct_answer:
            await interaction.response.send_message("Correct!", ephemeral=True)
        else:
            await interaction.response.send_message(f"Incorrect! The correct answer was: {self.correct_answer}", ephemeral=True)

class Fun(commands.Cog, name="fun"):
    def __init__(self, bot) -> None:
        self.bot = bot

    def get_trivia_question(self):
        url = "https://opentdb.com/api.php"
        params = {
            'amount': 1,  # Number of questions
            'type': 'multiple'  # Type of question
        }
        response = requests.get(url, params=params)
        data = response.json()

        if data['response_code'] == 0:
            question = data['results'][0]['question']
            correct_answer = data['results'][0]['correct_answer']
            incorrect_answers = data['results'][0]['incorrect_answers']
            options = [correct_answer] + incorrect_answers
            random.shuffle(options)  # Shuffle to randomize answer positions

            # Clean the text
            question = html.unescape(question)
            correct_answer = html.unescape(correct_answer)
            options = [html.unescape(option) for option in options]

            return question, correct_answer, options
        else:
            return None, None, None

    @commands.hybrid_command(name='trivia', description="Play a trivia game!")
    async def trivia(self, context: Context):
        question, correct_answer, options = self.get_trivia_question()
        if question:
            buttons = [TriviaButton(label=option, answer=option, correct_answer=correct_answer,
                                    style=discord.ButtonStyle.primary) for option in options]
            view = discord.ui.View()
            for button in buttons:
                view.add_item(button)

            embed = discord.Embed(title="Trivia Time!", description=question, color=0x00FFFF)
            await context.send(embed=embed, view=view)
        else:
            await context.send("Failed to get a trivia question. Please try again later.")

    def caesar_cipher(self, text, shift, decrypt):
        if decrypt:
            shift = -shift
        return ''.join(
            chr((ord(char) - 97 + shift) % 26 + 97) if char.isalpha() else char
            for char in text.lower()
        )


    @commands.hybrid_command(name='encrypt', description="Encrypts a message.")
    async def encrypt(self, context: Context, shift: int, *, message: str):
        encrypted_message = self.caesar_cipher(message, shift, decrypt=False)
        await context.send(f"Encrypted: {encrypted_message}")

    @commands.hybrid_command(name='decrypt', description="Decrypts a message.")
    async def decrypt(self, context: Context, shift: int, *, message: str):
        decrypted_message = self.caesar_cipher(message, shift, decrypt=True)
        await context.send(f"Decrypted: {decrypted_message}")


    @commands.hybrid_command(name="calculator", description="Here's a calculator function for you to use!")
    async def calculator(self, context: Context):

        def add(x, y):
            return x + y

        def subtract(x, y):
            return x - y

        def multiply(x, y):
            return x * y

        def divide(x, y):
            return x / y

        await context.send("Welcome! Select operation:\n1. Add\n2. Subtract\n3. Multiply\n4. Divide")

        def check(m):
            return m.author == context.author and m.channel == context.channel

        try:
            choice_msg = await self.bot.wait_for('message', check=check, timeout=60.0)
            choice = choice_msg.content

            if choice in ('1', '2', '3', '4'):
                await context.send("Enter first number:")
                num1_msg = await self.bot.wait_for('message', check=check, timeout=60.0)
                num1 = float(num1_msg.content)

                await context.send("Enter second number:")
                num2_msg = await self.bot.wait_for('message', check=check, timeout=60.0)
                num2 = float(num2_msg.content)

                if choice == '1':
                    result = add(num1, num2)
                    await context.send(f"{num1} + {num2} = {result}")

                elif choice == '2':
                    result = subtract(num1, num2)
                    await context.send(f"{num1} - {num2} = {result}")

                elif choice == '3':
                    result = multiply(num1, num2)
                    await context.send(f"{num1} * {num2} = {result}")

                elif choice == '4':
                    if num2 == 0:
                        await context.send("Cannot divide by zero!")
                    else:
                        result = divide(num1, num2)
                        await context.send(f"{num1} / {num2} = {result}")
            else:
                await context.send("Invalid choice! Please enter 1, 2, 3, or 4.")

        except asyncio.TimeoutError:
            await context.send("You took too long to respond! Please try again.")

    @commands.hybrid_command(name="hello", description="greets you based on the time of the day!")
    async def hello(self, context: Context):
        current_time = datetime.now().hour

        if 6 <= current_time < 12:
            await context.send("Good morning!")
        elif 12 <= current_time < 17:
            await context.send("Good afternoon!")
        elif 17 <= current_time < 21:
            await context.send("Good evening!")
        else:
            await context.send("It's getting late, consider going to sleep")

    @commands.hybrid_command(name="age", description="calculates the age")
    async def age(self, context: Context, birthdate: str) -> None:
        birthdate = datetime.strptime(birthdate, "%d-%m-%Y")
        today = datetime.today()
        age = ((today - birthdate).days / 365)
        await context.send(f"You are {int(age)} years old!")

    @commands.hybrid_command(name="centimeters", description="converts inches to centimeters")
    async def centimeters(self, context: Context, inches: float):
        centimeters = (inches * 2.54)
        await context.send(f"that is {float(centimeters)} centimeters")

    @commands.hybrid_command(name='temperature', description="Converts degree fahrenheit to degree celsius.")
    async def temperature(self, context: Context, fahrenheit: float) -> None:
        celsius = (fahrenheit - 32) * 5 / 9
        await context.send(f'{fahrenheit} degree F is {celsius} degree celsius.')

    @commands.hybrid_command(name="randomfact", description="Get a random fact.")
    async def randomfact(self, context: Context) -> None:
        """
        Get a random fact.

        :param context: The hybrid command context.
        """
        # This will prevent your bot from stopping everything when doing a web request - see: https://discordpy.readthedocs.io/en/stable/faq.html#how-do-i-make-a-web-request
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://uselessfacts.jsph.pl/random.json?language=en"
            ) as request:
                if request.status == 200:
                    data = await request.json()
                    embed = discord.Embed(description=data["text"], color=0xD75BF4)
                else:
                    embed = discord.Embed(
                        title="Error!",
                        description="There is something wrong with the API, please try again later",
                        color=0xE02B2B,
                    )
                await context.send(embed=embed)

    @commands.hybrid_command(
        name="coinflip", description="Make a coin flip, but give your bet before."
    )
    async def coinflip(self, context: Context) -> None:
        """
        Make a coin flip, but give your bet before.

        :param context: The hybrid command context.
        """
        buttons = Choice()
        embed = discord.Embed(description="What is your bet?", color=0xBEBEFE)
        message = await context.send(embed=embed, view=buttons)
        await buttons.wait()  # We wait for the user to click a button.
        result = random.choice(["heads", "tails"])
        if buttons.value == result:
            embed = discord.Embed(
                description=f"Correct! You guessed `{buttons.value}` and I flipped the coin to `{result}`.",
                color=0xBEBEFE,
            )
        else:
            embed = discord.Embed(
                description=f"Woops! You guessed `{buttons.value}` and I flipped the coin to `{result}`, better luck next time!",
                color=0xE02B2B,
            )
        await message.edit(embed=embed, view=None, content=None)

    @commands.hybrid_command(
        name="rps", description="Play the rock paper scissors game against the bot."
    )
    async def rock_paper_scissors(self, context: Context) -> None:
        """
        Play the rock paper scissors game against the bot.

        :param context: The hybrid command context.
        """
        view = RockPaperScissorsView()
        await context.send("Please make your choice", view=view)


async def setup(bot) -> None:
    await bot.add_cog(Fun(bot))
