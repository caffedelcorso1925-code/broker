import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- CONFIGURAZIONE INIZIALE ---
# Spostiamo tutto all'inizio, fuori da ogni blocco
TOKEN_BOT = "IL_TUO_TOKEN_QUI"
CHAT_ID_UTENTE = "IL_TUO_CHAT_ID_QUI"

# Definiamo i titoli subito, così Python non può non trovarli
titoli = [
    'AAPL', 'NVDA', 'TSLA', 'AMZN', 'MSFT', 'META', 'GOOGL', 'AMD', 'PLTR', 
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'GC=F', 'RACE.MI', 'ENI.MI', 'UCG.MI'
]

# Impostazione pagina
st.set_page_config(page_title="Robot Investitore", page_icon="⚡")
st.title("⚡ Robot Dinamico 10€")

def invia_telegram(messaggio):
    try:
        url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
        payload = {"chat_id": CHAT_ID_UTENTE, "text": messaggio}
        requests.post(url, data=payload)
    except Exception as e:
        st.error(f"Errore invio Telegram: {e}")

# --- LOGICA DELL'APP ---
if st.button('🚀 Avvia Scansione'):
    italy_tz = pytz.timezone("Europe/Rome")
    progress_bar = st.progress(0)
    
    for i, t in enumerate(titoli):
        try:
            df = yf.download(t, period="2mo", interval="1d", progress=False)
            
            if not df.empty and len(df) > 20:
                # Gestione corretta dei dati per evitare errori di formato
                chiusura = df['Close'].squeeze()
                
                # Calcolo RSI
                delta = chiusura.diff()
                up = delta.clip(lower=0)
                down = -1 * delta.clip(upper=0)
                ema_up = up.ewm(com=13, adjust=False).mean()
                ema_down = down.ewm(com=13, adjust=False).mean()
                rs = ema_up / ema_down
                rsi = 100 - (100 / (1 + rs))
                
                rsi_attuale = float(rsi.iloc[-1])
                prezzo_attuale = float(chiusura.iloc[-1])
                ora_esatta = datetime.now(italy_tz).strftime("%H:%M:%S")

                if rsi_attuale < 40:
                    msg = f"🟢 SEGNALE ORE {ora_esatta}\nTitolo: {t}\nPrezzo: {prezzo_attuale:.2f}€\nRSI: {rsi_attuale:.1f}"
                    st.success(msg)
                    invia_telegram(msg)
                else:
                    st.info(f"⚪ {t}: RSI {rsi_attuale:.1f}")
            
        except Exception as e:
            st.warning(f"Salto {t} per errore dati")
            
        progress_bar.progress((i + 1) / len(titoli))
    
    st.success("Scansione completata!")
