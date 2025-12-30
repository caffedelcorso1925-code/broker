import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- CONFIGURAZIONE ---
TOKEN_BOT = "IL_TUO_TOKEN_QUI"
CHAT_ID_UTENTE = "IL_TUO_CHAT_ID_QUI"

# Questa è la lista 'titoli' che causava l'errore. Ora è protetta.
titoli_lista = ['AAPL', 'NVDA', 'TSLA', 'AMZN', 'MSFT', 'BTC-USD', 'ETH-USD', 'SOL-USD', 'GC=F']

st.set_page_config(page_title="Robot 10 Euro", page_icon="🤖")
st.title("🤖 Robot Massima Resa")

def invia_telegram(messaggio):
    try:
        url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
        payload = {"chat_id": CHAT_ID_UTENTE, "text": messaggio}
        requests.post(url, data=payload)
    except Exception as e:
        pass

# --- LOGICA ---
if st.button('🎯 Esegui Scansione Ora'):
    italy_tz = pytz.timezone("Europe/Rome")
    st.write("Analisi in corso...")
    
    for t in titoli_lista:
        try:
            dati = yf.download(t, period="2mo", interval="1d", progress=False)
            if not dati.empty and len(dati) > 20:
                chiusura = dati['Close'].squeeze()
                delta = chiusura.diff()
                up, down = delta.clip(lower=0), -1 * delta.clip(upper=0)
                ema_up = up.ewm(com=13, adjust=False).mean()
                ema_down = down.ewm(com=13, adjust=False).mean()
                rsi = 100 - (100 / (1 + (ema_up / ema_down)))
                
                valore_rsi = float(rsi.iloc[-1])
                prezzo = float(chiusura.iloc[-1])
                ora = datetime.now(italy_tz).strftime("%H:%M")

                if valore_rsi < 40:
                    testo = f"🟢 {t} SOTTOCOSTO!\nPrezzo: {prezzo:.2f}€\nRSI: {valore_rsi:.1f}\nOre: {ora}"
                    st.success(testo)
                    invia_telegram(testo)
                else:
                    st.info(f"⚪ {t}: RSI {valore_rsi:.1f}")
        except:
            continue
    st.success("Fine analisi.")
