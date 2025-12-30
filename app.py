import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import pytz

# 1. DATI TELEGRAM (Inserisci i tuoi qui)
TOKEN_BOT = "IL_TUO_TOKEN_QUI"
CHAT_ID_UTENTE = "IL_TUO_CHAT_ID_QUI"

# 2. DEFINIZIONE TITOLI (Spostata qui per evitare il NameError)
titoli = [
    'AAPL', 'NVDA', 'TSLA', 'AMZN', 'MSFT', 'META', 'GOOGL', 'AMD', 'PLTR', 
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'GC=F', 'RACE.MI', 'ENI.MI', 'UCG.MI'
]

italy_tz = pytz.timezone("Europe/Rome")

def invia_telegram(messaggio):
    try:
        url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
        payload = {"chat_id": CHAT_ID_UTENTE, "text": messaggio}
        requests.post(url, data=payload)
    except Exception as e:
        st.error(f"Errore Telegram: {e}")

# INTERFACCIA APP
st.set_page_config(page_title="Robot Daily Trader", page_icon="⚡")
st.title("⚡ Robot Dinamico 10€")

# Bottone per avviare
if st.button('🚀 Avvia Scansione Dinamica'):
    progress_bar = st.progress(0)
    for i, t in enumerate(titoli):
        df = yf.download(t, period="2mo", interval="1d", progress=False)
        
        if not df.empty and len(df) > 20:
            # Calcolo RSI
            chiusura = df['Close'].squeeze()
            delta = chiusura.diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            rs = ema_up / ema_down
            rsi = 100 - (100 / (1 + rs))
            
            rsi_attuale = float(rsi.iloc[-1])
            prezzo = float(chiusura.iloc[-1])
            ora_segnale = datetime.now(italy_tz).strftime("%H:%M:%S")

            if rsi_attuale < 40:
                msg = f"🟢 SEGNALE ORE {ora_segnale}\nTitolo: {t}\nPrezzo: {prezzo:.2f}\nRSI: {rsi_attuale:.1f}"
                st.success(msg)
                invia_telegram(msg)
            else:
                st.info(f"⚪ {t}: RSI {rsi_attuale:.1f}")
        
        progress_bar.progress((i + 1) / len(titoli))
    
    st.success("Scansione completata!")
