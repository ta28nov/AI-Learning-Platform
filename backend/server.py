import sys
import os

# Add BELEARNINGAI to path
sys.path.insert(0, '/app/BELEARNINGAI')
os.chdir('/app/BELEARNINGAI')

# Load .env from BELEARNINGAI directory
from dotenv import load_dotenv
load_dotenv('/app/BELEARNINGAI/.env')

from app.main import app
