import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- CONFIGURAZIONE TELEGRAM ---
TOKEN_BOT = "IL_TUO_TOKEN_QUI"
CHAT_ID_UTENTE = "IL_TUO_CHAT_ID_QUI"
italy_tz = pytz.timezone("Europe/Rome")

def invia_telegram(messaggio):
    try:
        url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
        payload = {"chat_id": CHAT_ID_UTENTE, "text": messaggio}
        requests.post(url, data=payload, timeout=5)
    except:
        pass

# --- CONFIGURAZIONE APP ---
st.set_page_config(page_title="Robot Light 35", page_icon="⚡")
st.title("⚡ Robot 52 Titoli - Soglia RSI 35")
st.write(f"Scansione rapida testuale. Ora: {datetime.now(italy_tz).strftime('%H:%M:%S')}")

# --- LISTA 52 TITOLI ---
titoli = [
    'AAPL', 'NVDA', 'TSLA', 'AMZN', 'MSFT', 'META', 'GOOGL', 'AMD', 'PLTR', 'NFLX', 
    'ARM', 'SMCI', 'AVGO', 'INTC', 'ORCL', 'SNOW', 'BABA', 'UBER', 'COIN', 'SHOP',
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'DOGE-USD', 'ADA-USD', 'XRP-USD', 'DOT-USD', 'LINK-USD',
    'QQQ', 'SPY', 'GC=F', 'CL=F', 'RACE.MI', 'ENI.MI', 'UCG.MI', 'ISP.MI', 'STLAM.MI', 
    'STM.MI', 'EGP.MI', 'PST.MI', 'LDO.MI', 'G.MI', 'GME', 'AMC', 'PYPL', 'DIS', 'NIO', 
    'SQ', 'MSTR', 'MDB', 'AIBOT', 'V'
]

# --- AVVIO SCANSIONE ---
if st.button('🚀 AVVIA SCANSIONE RAPIDA'):
    progress_bar = st.progress(0)
    segnali_trovati = 0
    
    for i, t in enumerate(titoli):
        # Scarichiamo dati minimi per velocità
        df = yf.download(t, period="30d", interval="1d", progress=False)
        
        if not df.empty and len(df) > 14:
            # Fix per colonne Yahoo Finance
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Calcolo RSI
            delta = df['Close'].diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            rs = ema_up / ema_down
            rsi_attuale = float(100 - (100 / (1 + rs)).iloc[-1])
            prezzo_attuale = float(df['Close'].iloc[-1])
            ora_segnale = datetime.now(italy_tz).strftime("%H:%M:%S")

            # --- SOGLIA IMPOSTATA A 35 ---
            if rsi_attuale < 35:
                segnali_trovati += 1
                emoji = "🚨" if rsi_attuale < 25 else "🟢"
                
                # Visualizzazione in App
                st.success(f"{emoji} **{t}** | Prezzo: **{prezzo_attuale:.2f}** | RSI: **{rsi_attuale:.1f}**")
                
                # Notifica Telegram
                msg = f"{emoji} SEGNALE {t}\nPrezzo: {prezzo_attuale:.2f}\nRSI: {rsi_attuale:.1f}\nOre: {ora_segnale}"
                invia_telegram(msg)
            else:
                st.text(f"⚪ {t}: RSI {rsi_attuale:.1f}")
        
        progress_bar.progress((i + 1) / len(titoli))
    
    if segnali_trovati == 0:
        st.info("Nessun titolo sotto RSI 35 al momento.")
    else:
        st.success(f"Scansione completata! Trovati {segnali_trovati} segnali.")           
