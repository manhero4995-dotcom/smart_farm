# ============================================================
# boot.py — أول ملف بيشتغل تلقائياً عند تشغيل الـ ESP32
# قبل main.py بيشتغل
# مهمته: يقول للـ Python فين يلاقي الملفات بتاعتنا
# ============================================================

import sys
import gc

# بنقول للـ Python:
# لما حد يعمل "import sensors" → دوّر في /app
# لما حد يعمل "import ssd1306" → دوّر في /lib
sys.path.append('/app')
sys.path.append('/lib')

# تفعيل الـ garbage collector
# ده بيمسح الـ RAM اللي مش بتتستخدم تلقائياً
gc.enable()

print("[boot] ready - RAM free:", gc.mem_free())
