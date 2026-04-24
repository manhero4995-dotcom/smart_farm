

# ================
# 🥾 boot.py 
# ================

import sys
import gc

sys.path.append('/app')
sys.path.append('/lib')

gc.enable()

print("[boot] ready — RAM free:", gc.mem_free())
