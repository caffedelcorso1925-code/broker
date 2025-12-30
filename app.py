import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- 1. CONFIGURAZIONE CREDENZIALI ---
TOKEN_BOT = "IL_TUO_TOKEN_QUI"
CHAT_ID_UTENTE = "IL_TUO_CHAT_ID_QUI"

# --- 2. DEFINIZIONE TITOLI (Fissa e globale) ---
# Questa lista DEVE stare fuori da ogni funzione o bottone
titoli = ['AAPL', 'NVDA', 'TSLA', 'AMZN', 'MSFT', 'BTC-USD', 'ETH-USD', 'SOL-USD', 'GC=F']

# --- 3. FUNZIONI DI SERVIZIO ---
def invia_telegram(messaggio):
    try:
        url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
        payload = {"chat_id": CHAT_ID_UTENTE, "text": messaggio}
        requests.post(url, data=payload)
    except Exception as e:
        st.error(f"Errore Telegram: {e}")

# --- 4. INTERFACCIA UTENTE ---
st.set_page_config(page_title="Robot Daily", page_icon="⚡")
st.title("🚀 Robot Dinamico 10€")
st.write("Analisi RSI in tempo reale")

# --- 5. LOGICA DI SCANSIONE ---
if st.button('🎯 Avvia Scansione Ora'):
    italy_tz = pytz.timezone("Europe/Rome")
    progress_bar = st.progress(0)
    
    # Usiamo titoli definita sopra alla riga 13
    for i, t in enumerate(titoli):
        try:
            # Scarico i dati
            df = yf.download(t, period="2mo", interval="1d", progress=False)
            
            if not df.empty and len(df) > 20:
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

                # Soglia dinamica a 40
                if rsi_attuale < 40:
                    msg = f"🟢 OCCASIONE: {t}\nPrezzo: {prezzo_attuale:.2f}€\nRSI: {rsi_attuale:.1f}\nOra: {ora_esatta}"
                    st.success(msg)
                    invia_telegram(msg)
                else:
                    st.info(f"⚪ {t}: RSI {rsi_attuale:.1f}")
            
        except Exception as e:
            st.warning(f"Errore su {t}: {e}")
            
        # Aggiorno la barra
        progress_bar.progress((i + 1) / len(titoli))
    
    st.success("Scansione completata!")
