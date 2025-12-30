import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- 1. CONFIGURAZIONE CREDENZIALI ---
TOKEN_BOT = "IL_TUO_TOKEN_QUI"
CHAT_ID_UTENTE = "IL_TUO_CHAT_ID_QUI"

# --- 2. LISTA MAX OPPORTUNITÀ (30+ Strumenti) ---
lista_strumenti = [
    # Cripto
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD', 'DOGE-USD', 'LINK-USD',
    # Azioni USA Tech & AI
    'AAPL', 'NVDA', 'TSLA', 'AMZN', 'MSFT', 'META', 'GOOGL', 'AMD', 'PLTR', 'NFLX', 'COIN', 'MSTR',
    # Azioni Italia
    'RACE.MI', 'ENI.MI', 'UCG.MI', 'ISP.MI', 'STLAM.MI', 'ENEL.MI',
    # Materie Prime & Valute
    'GC=F', 'SI=F', 'CL=F', 'EURUSD=X'
]

def invia_telegram(messaggio):
    try:
        url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
        payload = {"chat_id": CHAT_ID_UTENTE, "text": messaggio}
        requests.post(url, data=payload)
    except:
        pass

# --- 3. INTERFACCIA ---
st.set_page_config(page_title="Robot Pro 10€", page_icon="💰")
st.title("💰 Robot Investitore Dinamico")
st.write("Scansione avanzata per trovare titoli 'sotto costo'.")

if st.button('🚀 AVVIA SCANSIONE GLOBALE'):
    italy_tz = pytz.timezone("Europe/Rome")
    risultati = []
    
    st.write("🔍 Analisi di 30+ mercati in corso...")
    progresso = st.progress(0)
    
    for i, t in enumerate(lista_strumenti):
        try:
            # Scarico dati (2 mesi per RSI preciso)
            df = yf.download(t, period="2mo", interval="1d", progress=False)
            
            if not df.empty and len(df) > 14:
                # Pulizia MultiIndex
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # Calcolo RSI
                chiusura = df['Close'].astype(float)
                delta = chiusura.diff()
                up = delta.clip(lower=0)
                down = -1 * delta.clip(upper=0)
                ema_up = up.ewm(com=13, adjust=False).mean()
                ema_down = down.ewm(com=13, adjust=False).mean()
                rs = ema_up / ema_down
                rsi_serie = 100 - (100 / (1 + rs))
                
                rsi_attuale = round(float(rsi_serie.iloc[-1]), 2)
                prezzo = round(float(chiusura.iloc[-1]), 2)
                
                # Salviamo i dati per ordinarli dopo
                risultati.append({
                    'ticker': t,
                    'prezzo': prezzo,
                    'rsi': rsi_attuale
                })
        except:
            continue
        progresso.progress((i + 1) / len(lista_strumenti))

    # --- 4. VISUALIZZAZIONE ORDINATA PER RSI ---
    # Ordiniamo la lista dal più basso al più alto
    risultati_ordinati = sorted(risultati, key=lambda x: x['rsi'])
    
    st.write("### 📊 Risultati (dal più scontato al più caro)")
    
    for r in risultati_ordinati:
        t = r['ticker']
        p = r['prezzo']
        rsi = r['rsi']
        ora = datetime.now(italy_tz).strftime("%H:%M")

        if rsi < 35:
            msg = f"🟩 **COMPRA ORA** | {t} | Prezzo: {p} | **RSI: {rsi}**"
            st.success(msg)
            invia_telegram(f"🟢 OCCASIONE: {t}\nPrezzo: {p}\nRSI: {rsi}\nOre: {ora}")
        elif 35 <= rsi < 45:
            st.write(f"⬜ **ATTENZIONE** | {t} | Prezzo: {p} | **RSI: {rsi}**")
        elif rsi > 70:
            st.error(f"🟥 **VENDI/EVITA** | {t} | Prezzo: {p} | **RSI: {rsi}**")
        else:
            st.info(f"🔵 NEUTRO | {t} | Prezzo: {p} | RSI: {rsi}")

    st.success("Scansione completata. Controlla Telegram!")
