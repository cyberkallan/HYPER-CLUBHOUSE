#!/data/data/com.termux/files/usr/bin/bash

# HyperCLUB Bot - Termux Installation Script
# by cyberkallan

echo "🤖 HyperCLUB Bot v2.0 - Termux Installer"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_header() {
    echo -e "${CYAN}$1${NC}"
}

# Check if running in Termux
if ! command -v pkg &> /dev/null; then
    print_error "This script must be run in Termux!"
    print_warning "Please install Termux from F-Droid and try again."
    exit 1
fi

print_header "🚀 Starting HyperCLUB Bot Installation..."

# Update package list
print_status "Updating package list..."
pkg update -y

# Install Python
print_status "Installing Python..."
pkg install python -y

# Install pip if not present
if ! command -v pip &> /dev/null; then
    print_status "Installing pip..."
    pkg install python-pip -y
fi

# Install required Python packages
print_status "Installing Python dependencies..."
pip install requests

# Create bot directory
BOT_DIR="$HOME/hyperclub-bot"
print_status "Creating bot directory: $BOT_DIR"
mkdir -p "$BOT_DIR"
cd "$BOT_DIR"

# Download the bot
print_status "Downloading HyperCLUB Bot..."
curl -L -o hyperCLUB_bot_termux.py "https://raw.githubusercontent.com/cyberkallan/hyperclub-bot/main/hyperCLUB_bot_termux.py"

# Create sample configuration files
print_status "Creating configuration files..."

# Launch message
cat > launch_message.txt << 'EOF'
🎉 HyperCLUB Bot v2.0 launched and Loving each members❤️
🤖 Most Advanced Clubhouse Bot by cyberkallan
⚡ Premium experience with cutting-edge features
EOF

# Speaker welcome messages
cat > speaker_welcome.txt << 'EOF'
🎤 Welcome on stage, {name}! 👏
🌟 Great to see you as a speaker!
💫 You're now part of our amazing community!
EOF

# VIP welcome messages
cat > vip_welcome.txt << 'EOF'
👑 Welcome VIP {name}! 🎉
⭐ You're our special guest today!
💎 Enjoy your premium experience!
EOF

# Periodic messages
cat > periodic_messages.txt << 'EOF'
🎵 Remember to follow our community guidelines!
🌟 Don't forget to invite your friends!
💫 Stay connected with our amazing community!
EOF

# Empty user lists
cat > vip_users.txt << 'EOF'
# Add VIP user IDs here (one per line)
# Example: 123456789
EOF

cat > blocked_users.txt << 'EOF'
# Add blocked user IDs here (one per line)
# Example: 987654321
EOF

# Empty token file
cat > token.txt << 'EOF'
# Add your Clubhouse token here
EOF

# Create launcher script
cat > run_bot.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

echo "🤖 Starting HyperCLUB Bot..."
echo "============================"
echo ""

cd "$HOME/hyperclub-bot"
python hyperCLUB_bot_termux.py
EOF

chmod +x run_bot.sh

# Create quick start guide
cat > QUICK_START.md << 'EOF'
# 🚀 HyperCLUB Bot - Quick Start Guide

## 📱 **Termux Setup Complete!**

Your HyperCLUB Bot is now installed and ready to use!

### 🎯 **Next Steps:**

1. **Get License Key**
   - Contact @deno_tech on Telegram
   - Purchase your preferred plan
   - Receive your unique license key

2. **Configure Bot**
   - Edit `token.txt` - Add your Clubhouse token
   - Edit `launch_message.txt` - Customize startup message
   - Edit `speaker_welcome.txt` - Customize speaker welcomes
   - Edit `vip_welcome.txt` - Customize VIP welcomes

3. **Run Bot**
   ```bash
   cd ~/hyperclub-bot
   ./run_bot.sh
   ```

### 📁 **Files Created:**
- `hyperCLUB_bot_termux.py` - Main bot script
- `run_bot.sh` - Easy launcher script
- `launch_message.txt` - Bot startup message
- `speaker_welcome.txt` - Speaker welcome messages
- `vip_welcome.txt` - VIP user messages
- `periodic_messages.txt` - Periodic announcements
- `vip_users.txt` - VIP users list
- `blocked_users.txt` - Blocked users list
- `token.txt` - Bot token storage

### 🆘 **Need Help?**
- **Telegram Support**: @deno_tech
- **Documentation**: Check the main README
- **Issues**: Report on GitHub

### 🎉 **Enjoy Your Premium Bot Experience!**
EOF

print_success "Installation completed successfully!"
echo ""
print_header "🎉 **INSTALLATION COMPLETE!**"
echo ""
echo -e "${GREEN}✅ Python installed${NC}"
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo -e "${GREEN}✅ Bot downloaded${NC}"
echo -e "${GREEN}✅ Configuration files created${NC}"
echo -e "${GREEN}✅ Launcher script created${NC}"
echo ""
print_header "📁 **Files Location:**"
echo -e "${CYAN}Bot Directory:${NC} $BOT_DIR"
echo ""
print_header "🚀 **To Start the Bot:**"
echo -e "${YELLOW}cd ~/hyperclub-bot${NC}"
echo -e "${YELLOW}./run_bot.sh${NC}"
echo ""
print_header "📖 **Quick Start Guide:**"
echo -e "${CYAN}cat ~/hyperclub-bot/QUICK_START.md${NC}"
echo ""
print_warning "⚠️  Don't forget to get your license key from @deno_tech on Telegram!"
echo ""
print_success "🎉 HyperCLUB Bot is ready to use!"
