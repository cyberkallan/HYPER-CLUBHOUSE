import requests,time,random,os,json,signal,sys,uuid,platform,base64,hashlib,hmac,subprocess
from types import FunctionType
from datetime import datetime

# ================== HYPERCLUB-BOT ==================
_xor_key = 0x42
def _xor_decode(s):
    try:
        return base64.b64decode(s).decode()
    except Exception:
        return s

def _split_decode(parts):
    return ''.join(_xor_decode(p) for p in parts)

# Obfuscated sensitive data
_obf_data = {
    'url': ['aHR0cHM6Ly9uZW9jYXQuc3RvcmUvd2Vic2l0ZS9hcGkvdmFsaWRhdGVfbGljZW5zZS5waHA='],
    'api_base': ['aHR0cHM6Ly93d3cuY2x1YmhvdXNlYXBpLmNvbS9hcGkv'],
    'endpoints': {
        'validate': ['dmFsaWRhdGVfbGljZW5zZS5waHA='],
        'channel': ['Z2V0X2NoYW5uZWw='],
        'invite': ['aW52aXRlX3NwZWFrZXI='],
        'message': ['c2VuZF9jaGFubmVsX21lc3NhZ2U='],
        'leave': ['bGVhdmVfY2hhbm5lbA=='],
        # decoys
        'dec1': ['c2VjdXJlX3Rlc3Q='],
        'dec2': ['c3VwZXJfc2VjcmV0X2VuZHBvaW50']
    },
    'params': {
        'license': ['bGljZW5zZV9rZXk='],
        'device_id': ['ZGV2aWNlX2lk'],
        'device_name': ['ZGV2aWNlX25hbWU='],
        'channel': ['Y2hhbm5lbA=='],
        'user_id': ['dXNlcl9pZA=='],
        'message': ['bWVzc2FnZQ=='],
        'valid': ['dmFsaWQ='],
        'error': ['ZXJyb3I='],
        'auth': ['QXV0aG9yaXphdGlvbg=='],
        'token': ['VG9rZW4g']
    },
    'sec': ['aGNfY2xpZW50X3NlY3JldF8yMDI0']
}

def _get_obf_value(category, key=None):
    if key:
        return _split_decode(_obf_data[category][key])
    return _split_decode(_obf_data[category])

# ================== SECURITY HELPERS ==================
def _get_machine_fingerprint():
    components = []
    try:
        # Windows MachineGuid
        if sys.platform.startswith('win'):
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Cryptography") as k:
                    mg, _ = winreg.QueryValueEx(k, "MachineGuid")
                    components.append(str(mg))
            except Exception:
                pass
            try:
                out = subprocess.check_output(["wmic", "bios", "get", "serialnumber"], stderr=subprocess.STDOUT, shell=True)
                components.append(out.decode(errors='ignore').strip())
            except Exception:
                pass
        # Linux/Android machine-id
        for path in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
            try:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        components.append(f.read().strip())
                        break
            except Exception:
                pass
        # Android serial
        try:
            out = subprocess.check_output(["getprop", "ro.serialno"], stderr=subprocess.STDOUT)
            components.append(out.decode(errors='ignore').strip())
        except Exception:
            pass
    except Exception:
        pass
    try:
        components.append(hex(uuid.getnode()))
    except Exception:
        pass
    base = "|".join([c for c in components if c]) or (platform.system() + platform.node())
    return hashlib.sha256(base.encode()).hexdigest()

def _get_script_hash():
    try:
        p = os.path.abspath(__file__)
        with open(p, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return ""

def _anti_debug_checks():
    if sys.gettrace() is not None:
        return False
    suspicious = ["pydevd", "frida", "x64dbg", "gdb", "lldb", "ollydbg"]
    for name in suspicious:
        if name in str(sys.modules.keys()).lower():
            return False
    # environment red flags
    env_flags = ["PYTHONINSPECT", "PYTHONBREAKPOINT", "PYDEVD_LOAD_VALUES_ASYNC"]
    for k in env_flags:
        if os.environ.get(k):
            return False
    # basic VM heuristics
    vm_markers = ["vbox", "virtualbox", "vmware", "qemu", "kvm", "xen"]
    probe = (platform.platform() + " " + platform.machine() + " " + platform.node()).lower()
    if any(m in probe for m in vm_markers):
        return False
    return True

def _detect_monkey_patching():
    try:
        # ensure requests.post is from requests.api
        if getattr(requests.post, '__module__', '').split('.')[0] != 'requests':
            return False
        # ensure Session.post exists and is a function/method
        if not hasattr(requests.Session, 'post'):
            return False
    except Exception:
        return False
    return True

def _anti_step_timing_check():
    start = time.perf_counter()
    x = 0
    for i in range(10000):
        x ^= (i * 2654435761) & 0xFFFFFFFF
    elapsed = time.perf_counter() - start
    # if a debugger is stepping, this tiny loop will be abnormally slow
    return elapsed < 0.2

def _build_security_headers(license_key):
    ts = str(int(time.time()))
    nonce = uuid.uuid4().hex[:16]
    secret = _get_obf_value('sec')
    data = "|".join([license_key or "", _get_machine_fingerprint(), f"{platform.system()}-{platform.machine()}-{platform.node()}", ts, nonce, _get_script_hash()])
    try:
        proof = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
    except Exception:
        proof = ""
    return {
        'X-Client-Fingerprint': _get_machine_fingerprint(),
        'X-Client-Device': f"{platform.system()}-{platform.machine()}-{platform.node()}",
        'X-Client-TS': ts,
        'X-Client-Nonce': nonce,
        'X-Client-Proof': proof,
        'X-Client-Hash': _get_script_hash(),
        'X-Client-Version': '2.0'
    }

def _secure_session():
    s = requests.Session()
    try:
        s.trust_env = False  # ignore system proxies to reduce MITM/nuller hooks
        from requests.adapters import HTTPAdapter
        a = HTTPAdapter(pool_maxsize=4, max_retries=0, pool_connections=2)
        s.mount('https://', a)
        s.mount('http://', a)
    except Exception:
        pass
    return s

# ================== CONFIG ==================
LICENSE_SERVER_URL = _get_obf_value('url')
DEVICE_ID = _get_machine_fingerprint()
DEVICE_NAME = f"{platform.system()}-{platform.machine()}-{platform.node()}"
CHECK_INTERVAL = 5
WELCOME_COOLDOWN = 2
PROFILE_PATH = os.path.expanduser("~/.config/clubdeck/profiles.json")

class LicenseValidator:
    def __init__(self, server_url):
        self.server_url = server_url
        
    def validate_license(self, license_key):
        try:
            if not _anti_debug_checks():
                return False, "Security violation detected"
            if not _detect_monkey_patching():
                return False, "Environment integrity failed"
            if not _anti_step_timing_check():
                return False, "Abnormal execution timing"
            payload = {
                _get_obf_value('params', 'license'): license_key,
                _get_obf_value('params', 'device_id'): DEVICE_ID,
                _get_obf_value('params', 'device_name'): DEVICE_NAME
            }
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            try:
                headers.update(_build_security_headers(license_key))
            except Exception:
                pass
            
            session = _secure_session()
            response = session.post(self.server_url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get(_get_obf_value('params', 'valid')):
                    return True, data.get(_get_obf_value('params', 'message'), 'License valid')
                else:
                    return False, data.get(_get_obf_value('params', 'error'), 'Invalid license')
            else:
                data = response.json()
                return False, data.get(_get_obf_value('params', 'error'), 'Server error')
                
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
        except json.JSONDecodeError:
            return False, "Invalid server response"

class InputHandler:
    @staticmethod
    def get_license_key():
        print("\n" + "="*60)
        print("🤖 HyperCLUB Bot v2.0 - Most Advanced Clubhouse Bot")
        print("by cyberkallan | github/cyberkallan")
        print("="*60)
        print("\n🔑 LICENSE REQUIRED")
        print("Enter your license key to continue...")
        
        while True:
            license_key = input("\n📝 Enter your license key: ").strip()
            if license_key:
                return license_key
            else:
                print("❌ License key cannot be empty. Please try again.")

    @staticmethod
    def get_channel_id():
        print("\n📺 CHANNEL SETUP")
        return input("Enter Channel ID: ").strip()

    @staticmethod
    def get_token():
        print("\n🔐 TOKEN SETUP")
        print("Choose token mode:")
        print("1. Auto-fetch from Clubdeck profile")
        print("2. Manual input")
        
        choice = input("Enter 1 or 2: ").strip()
        
        if choice == "1":
            token = InputHandler.get_token_from_profile()
            if not token:
                print("⚠️ Failed to fetch token, fallback to manual input")
                return input("Enter token manually: ").strip()
            return token
        else:
            return input("Enter token manually: ").strip()

    @staticmethod
    def get_token_from_profile():
        try:
            with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                profiles = json.load(f)
            return profiles[0]["token"] if profiles else None
        except Exception as e:
            print("❌ Error loading token from profile:", e)
            return None

class HyperCLUBBot:
    def __init__(self):
        self.license_validator = LicenseValidator(LICENSE_SERVER_URL)
        self.license_key = None
        self.channel_id = None
        self.token = None
        self.headers = None
        self.user_cache = {}
        
    def setup(self):
        self.license_key = InputHandler.get_license_key()
        
        print("\n🔍 Validating license...")
        is_valid, message = self.license_validator.validate_license(self.license_key)
        
        if not is_valid:
            print(f"❌ {message}")
            print("\n💬 Contact @deno_tech on Telegram to purchase a license key.")
            input("\nPress Enter to exit...")
            sys.exit(1)
        
        print(f"✅ {message}")
        print("🎉 License validated successfully!")
        
        self.channel_id = InputHandler.get_channel_id()
        self.token = InputHandler.get_token()
        self.headers = {_get_obf_value('params', 'auth'): f"{_get_obf_value('params', 'token')}{self.token}"}
        
        self.load_messages()
        
    def load_messages(self):
        def load_lines(file):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    return [line.strip() for line in f if line.strip()]
            except:
                return []
        
        self.prefix_list = load_lines("emg1.txt")
        self.suffix_list = load_lines("emg2.txt")
        self.leave_list = load_lines("leaving.txt")
        
    def load_launch_message(self):
        try:
            with open("launch_message.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except:
            return "🤖 HyperCLUB Bot v2.0 launched and Loving each members❤️"
    
    def fetch_users(self):
        base_url = _get_obf_value('api_base')
        endpoint = _get_obf_value('endpoints', 'channel')
        url = f"{base_url}{endpoint}"
        
        try:
            payload = {_get_obf_value('params', 'channel'): self.channel_id}
            r = requests.post(url, headers=self.headers, json=payload)
            r.raise_for_status()
            return r.json().get("users", [])
        except Exception as e:
            print("❌ Error fetching users:", e)
            return []
    
    def invite_user(self, user_id):
        base_url = _get_obf_value('api_base')
        endpoint = _get_obf_value('endpoints', 'invite')
        url = f"{base_url}{endpoint}"
        
        payload = {_get_obf_value('params', 'channel'): self.channel_id, _get_obf_value('params', 'user_id'): user_id}
        try:
            r = requests.post(url, headers=self.headers, json=payload)
            r.raise_for_status()
            print(f"✅ Invited {user_id} to speakers")
        except Exception as e:
            print(f"❌ Error inviting {user_id}:", e)
    
    def send_message(self, text):
        base_url = _get_obf_value('api_base')
        endpoint = _get_obf_value('endpoints', 'message')
        url = f"{base_url}{endpoint}"
        
        payload = {_get_obf_value('params', 'channel'): self.channel_id, _get_obf_value('params', 'message'): text}
        try:
            requests.post(url, headers=self.headers, json=payload)
        except Exception as e:
            print("❌ Error sending message:", e)
    
    def leave_channel(self):
        base_url = _get_obf_value('api_base')
        endpoint = _get_obf_value('endpoints', 'leave')
        url = f"{base_url}{endpoint}"
        
        try:
            requests.post(url, headers=self.headers, json={_get_obf_value('params', 'channel'): self.channel_id})
        except Exception as e:
            print("❌ Error leaving channel:", e)
    
    def periodic_license_check(self):
        is_valid, message = self.license_validator.validate_license(self.license_key)
        if not is_valid:
            print(f"❌ License validation failed: {message}")
            print("💬 Contact @deno_tech on Telegram to purchase a license key.")
            return False
        return True
    
    def run(self):
        print("\n👀 HyperCLUB Bot started watching users...")
        known_users = set()
        last_license_check = time.time()
        
        while True:
            if time.time() - last_license_check > 300:
                if not self.periodic_license_check():
                    break
                last_license_check = time.time()
            
            users = self.fetch_users()
            current_ids = {u.get("user_id") for u in users if u.get("user_id")}
            
            new_users = [u for u in users if u.get("user_id") not in known_users]
            left_ids = known_users - current_ids
            
            if new_users:
                house_members = [u for u in new_users if u.get("is_house_member")]
                followers = [u for u in new_users if u.get("is_followed_by_speaker")]
                others = [u for u in new_users if not u.get("is_house_member") and not u.get("is_followed_by_speaker")]
                ordered_new = house_members + followers + others
                
                for user in ordered_new:
                    uid = user.get("user_id")
                    name = user.get("name") or user.get("username") or f"User {uid}"
                    if not uid:
                        continue
                    
                    self.user_cache[uid] = name
                    
                    if not user.get("is_speaker"):
                        self.invite_user(uid)
                        prefix = random.choice(self.prefix_list) if self.prefix_list else "👋"
                        suffix = random.choice(self.suffix_list) if self.suffix_list else "✨"
                        msg = f"{prefix} {name} {suffix}".strip()
                        self.send_message(msg)
                    else:
                        self.send_message(f"🎤 Welcome on stage, {name}! 👏")
                    
                    time.sleep(WELCOME_COOLDOWN)
            
            if left_ids:
                for uid in left_ids:
                    name = self.user_cache.get(uid, f"User {uid}")
                    template = random.choice(self.leave_list) if self.leave_list else "👋 {name} left the room."
                    goodbye_msg = template.replace("{name}", name)
                    self.send_message(goodbye_msg)
                    time.sleep(WELCOME_COOLDOWN)
            
            known_users = current_ids
            time.sleep(CHECK_INTERVAL)

def handle_exit(sig, frame):
    print("\n👋 Bot stopping...")
    if hasattr(bot, 'send_message'):
        bot.send_message("🤖 Bot stopped")
        bot.leave_channel()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_exit)
    
    bot = HyperCLUBBot()
    bot.setup()
    
    launch_msg = bot.load_launch_message()
    bot.send_message(launch_msg)
    
    bot.run()
