import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- 1. CONFIGURAZIONE CREDENZIALI ---
TOKEN_BOT = "IL_TUO_TOKEN_QUI"
CHAT_ID_UTENTE = "IL_TUO_CHAT_ID_QUI"

# --- 2. LISTA COMPLETA AGGIORNATA ---
lista_strumenti = [
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD', 'DOGE-USD', 'DOT-USD', 'LINK-USD', 'AVAX-USD',
    'AAPL', 'NVDA', 'TSLA', 'AMZN', 'MSFT', 'META', 'GOOGL', 'AMD', 'PLTR', 'NFLX', 'COIN', 'MSTR', 'SMCI', 'ARM', 'UBER',
    'DIS', 'NKE', 'SBUX', 'V', 'MA', 'BABA', 'PFE', 'T', 'VZ', 'PYPL', 'SQ',
    'RACE.MI', 'ENI.MI', 'UCG.MI', 'ISP.MI', 'STLAM.MI', 'ENEL.MI', 'PRY.MI', 'LDO.MI', 'MONC.MI',
    'GC=F', 'SI=F', 'CL=F', 'EURUSD=X', 'GBPUSD=X', '^GSPC', '^IXIC'
]

def invia_telegram(messaggio):
    try:
        url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
        payload = {"chat_id": CHAT_ID_UTENTE, "text": messaggio}
        requests.post(url, data=payload)
    except:
        pass

# --- 3. INTERFACCIA ---
st.set_page_config(page_title="Robot Pro", page_icon="💰")
st.title("💰 Robot Investitore Totale")

# Visualizza quanti titoli sono presenti per conferma
st.write(f"📊 Il database attuale contiene **{len(lista_strumenti)}** titoli.")

if st.button('🚀 AVVIA SCANSIONE GLOBALE'):
    italy_tz = pytz.timezone("Europe/Rome")
    risultati = []
    
    progresso = st.progress(0)
    status_text = st.empty()
    
    for i, t in enumerate(lista_strumenti):
        status_text.text(f"Analisi in corso: {t}...")
        try:
            df = yf.download(t, period="2mo", interval="1d", progress=False)
            
            if not df.empty and len(df) > 14:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                chiusura = df['Close'].astype(float)
                delta = chiusura.diff()
                up, down = delta.clip(lower=0), -1 * delta.clip(upper=0)
                ema_up = up.ewm(com=13, adjust=False).mean()
                ema_down = down.ewm(com=13, adjust=False).mean()
                rsi_serie = 100 - (100 / (1 + (ema_up / ema_down)))
                
                rsi_attuale = round(float(rsi_serie.iloc[-1]), 2)
                prezzo = round(float(chiusura.iloc[-1]), 2)
                
                risultati.append({'t': t, 'p': prezzo, 'r': rsi_attuale})
        except:
            continue
        progresso.progress((i + 1) / len(lista_strumenti))

    status_text.text("Scansione completata!")
    
    # Ordinamento e Visualizzazione
    risultati_ordinati = sorted(risultati, key=lambda x: x['r'])
    
    for r in risultati_ordinati:
        if r['r'] < 35:
            st.success(f"🟩 **ACQUISTO** | {r['t']} | Prezzo: {r['p']} | **RSI: {r['r']}**")
            invia_telegram(f"🟢 OCCASIONE: {r['t']}\nPrezzo: {r['p']}\nRSI: {r['r']}")
        elif r['r'] < 45:
            st.write(f"⬜ **ATTENZIONE** | {r['t']} | Prezzo: {r['p']} | RSI: {r['r']}")
        elif r['r'] > 70:
            st.error(f"🟥 **VENDI** | {r['t']} | Prezzo: {r['p']} | RSI: {r['r']}")
        else:
            st.info(f"🔵 NEUTRO | {r['t']} | Prezzo: {r['p']} | RSI: {r['r']}")
