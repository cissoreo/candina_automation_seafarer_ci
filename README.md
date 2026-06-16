# ⚓ Seafarer CV Analyzer v2

A Windows desktop app that reads seafarer CVs (PDF, Word, Excel), uses **Claude AI** to extract structured data, **automatically maps text → codes** using your reference tables, checks for duplicates in **Supabase**, lets you preview & edit, and inserts/updates 3 linked tables.

---

## ✨ Features

- ✅ Multi-file selection (PDF, DOCX, XLSX)
- ✅ Claude Haiku 4.5 for extraction → returns readable text
- ✅ **Local fuzzy code mapping** — text values auto-converted to your lookup codes (ranks, vessel types, certificates, etc.)
- ✅ **Interactive preview** with 4 tabs (Personal Info / Certificates / Sea Service / Raw Data)
- ✅ **Code-mapping column** shows the matched code next to each text value
- ✅ **Dropdowns for UNMATCHED items** — pick the correct code from the lookup list
- ✅ Duplicate detection (by name+surname+DOB OR email) → notification + update existing
- ✅ Real-time progress bar + token usage + cost tracker
- ✅ Single `.exe` — no Python needed on target machine

---

## 📋 Setup (one-time)

### 1. Create the database tables

In Supabase Dashboard:
1. Open **SQL Editor** → **New query**
2. Open `database_schema.sql`, copy ALL contents, paste into the editor
3. Click **Run**
4. You should now have 3 tables: `personal_information`, `certificates`, `experiences`

> ⚠ **Warning:** The schema script DROPS old tables first (clean install). Run it only on a fresh database, or back up your data first.

### 2. Get your API keys

- **Anthropic**: https://console.anthropic.com/ → API Keys → Create Key
- **Supabase**: Dashboard → Project Settings → API → copy URL + `service_role` key

### 3. Build the `.exe`

On Windows with Python 3.10+:

```bat
build_exe.bat
```

> ❓ **If you see errors:** make sure Python is in PATH. Reinstall Python and CHECK "Add Python to PATH".

The exe appears at: `dist\SeafarerCVAnalyzer.exe`

### 4. Configure

1. Copy `.env.example` into the `dist` folder (next to the .exe)
2. Rename it to `.env`
3. Open in Notepad and fill in your real API keys

---

## 🚀 How to use

1. Double-click `SeafarerCVAnalyzer.exe`
2. Click **📂 Select CV Files** → pick one or more CVs
3. Click **▶ Process Files**
4. For each CV, a **preview window** opens with 4 tabs:

   - **👤 Personal Information** — basic info, status, rank (with code mapping)
   - **📜 Certificates** — each cert as a card with category + auto-matched code
   - **⚓ Sea Service** — each vessel as a card with vessel type, engine, rank codes
   - **🔍 Raw Data** — what Claude returned (for debugging)

5. **Code matching legend**:
   - 🟢 **`✓ code: 569`** = text matched successfully to a lookup code
   - 🔴 **`⚠ UNMATCHED`** = no good match found → pick from the dropdown
   - **Empty** = no text in that field (skip)

6. Edit any field if needed
7. Click **💾 SAVE** (inserts new or updates existing) or **⏭ SKIP**

---

## 🧠 How the code-mapping works

Claude returns CV data as readable text:
```json
{"rank_text": "Deck Fitter", "type_text": "Cruise Ship", "engine_type_text": "MAN"}
```

The program then runs **fuzzy matching** locally (free, instant) against your lookup tables and converts to codes:
```
"Deck Fitter"   → 569 (DECK FITTER)
"Cruise Ship"   → 153 (Cruise Ship)
"MAN"           → 3 (MAN)
"Basic Safety Training" → 49 (Basic Safety Training (SOLAS))
"Passport"      → 105 (Passport)
```

These codes are stored in your Supabase database, exactly matching your existing data format.

---

## 💰 Cost breakdown

| Item | Per CV | Per 1,000 CVs |
|------|--------|---------------|
| Claude Haiku 4.5 API | ~$0.005–0.010 | ~$5–10 |
| Local code mapping | FREE | FREE |
| Supabase queries | within free tier | within free tier |

**Typical CV:** ~3,000 input tokens + ~1,500 output tokens = **$0.007 (~Rp 110)**

---

## 📁 File structure

```
seafarer_cv_analyzer/
├── main.py                       # GUI application
├── src/
│   ├── cv_extractor.py           # PDF/DOCX/XLSX → text (free, no API)
│   ├── claude_analyzer.py        # Claude API client
│   ├── code_mapper.py            # Fuzzy text → code matching
│   ├── lookups.py                # All 14 lookup tables (auto-generated)
│   └── supabase_manager.py       # Database operations
├── database_schema.sql           # Run ONCE in Supabase SQL editor
├── .env.example                  # Config template
├── requirements.txt              # Python dependencies
├── build_exe.bat                 # Build script
└── README.md                     # This file
```

---

## 🛠 Troubleshooting

**"`.env` file not found"**
→ Put `.env` in the same folder as the `.exe`. The filename must be exactly `.env` (not `.env.txt`).

**Many fields show "⚠ UNMATCHED"**
→ The CV uses unusual terminology. Use the dropdown next to each unmatched field to pick the right code.

**"violates foreign key constraint"** when saving
→ The `personal_information` insert failed. Check the log for the actual error (usually a unique constraint on name+DOB).

**Build script asks for password / errorlevel != 0**
→ Open Command Prompt → `cd D:\path\to\seafarer_cv_analyzer` → run `build_exe.bat` manually to see the real error.

**Want to test without `.exe`?**
→ `pip install -r requirements.txt` then `python main.py`.

---

## 🔒 Security notes

- The `.env` file contains API keys — **don't commit to git, don't share publicly**.
- For team use, consider Supabase Row-Level Security with restricted `anon` keys.
- The `.exe` does NOT encrypt the `.env`.
