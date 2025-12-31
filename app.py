import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- 1. CONFIGURAZIONE TELEGRAM ---
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

# --- 2. DEFINIZIONE LISTA TITOLI (Spostata in alto per evitare NameError) ---
titoli = [
    'AAPL', 'NVDA', 'TSLA', 'AMZN', 'MSFT', 'META', 'GOOGL', 'AMD', 'PLTR', 'NFLX', 
    'ARM', 'SMCI', 'AVGO', 'INTC', 'ORCL', 'SNOW', 'BABA', 'UBER', 'COIN', 'SHOP',
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'DOGE-USD', 'ADA-USD', 'XRP-USD', 'DOT-USD', 'LINK-USD',
    'QQQ', 'SPY', 'GC=F', 'CL=F', 'RACE.MI', 'ENI.MI', 'UCG.MI', 'ISP.MI', 'STLAM.MI', 
    'STM.MI', 'EGP.MI', 'PST.MI', 'LDO.MI', 'G.MI', 'GME', 'AMC', 'PYPL', 'DIS', 'NIO', 
    'SQ', 'MSTR', 'MDB', 'AIBOT', 'V'
]

# --- 3. CONFIGURAZIONE APP ---
st.set_page_config(page_title="Robot Trader 52", page_icon="⚖️")
st.title("⚖️ Robot 52 Titoli: Strategia 35/70")
st.write(f"Soglie: Compra < 35 | Vendi > 70. Ora: {datetime.now(italy_tz).strftime('%H:%M:%S')}")

# --- 4. LOGICA DI SCANSIONE ---
if st.button('🚀 AVVIA SCANSIONE'):
    progress_bar = st.progress(0)
    
    for i, t in enumerate(titoli):
        try:
            # Scarichiamo dati (30 giorni bastano)
            df = yf.download(t, period="30d", interval="1d", progress=False)
            
            if not df.empty and len(df) > 14:
                # Fix per colonne Yahoo Finance (MultiIndex)
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

                # --- VISUALIZZAZIONE RISULTATI ---
                
                if rsi_attuale < 35:
                    # VERDE - COMPRARE
                    st.success(f"🟢 **COMPRA {t}**: RSI {rsi_attuale:.1f} | Prezzo: {prezzo_attuale:.2f}")
                    invia_telegram(f"🚀 SEGNALE COMPRA\n{t}: {prezzo_attuale:.2f}\nRSI: {rsi_attuale:.1f}")
                
                elif rsi_attuale > 70:
                    # ROSSO - VENDERE
                    st.error(f"🔴 **VENDI {t}**: RSI {rsi_attuale:.1f} | Prezzo: {prezzo_attuale:.2f}")
                    invia_telegram(f"💰 SEGNALE VENDI\n{t}: {prezzo_attuale:.2f}\nRSI: {rsi_attuale:.1f}")
                
                else:
                    # BIANCO - STABILE
                    st.text(f"⚪ {t}: RSI {rsi_attuale:.1f} - Stabile")
                    
        except Exception as e:
            # Continua con il titolo successivo se c'è un errore
            continue
        
        progress_bar.progress((i + 1) / len(titoli))
    
    st.success("Scansione terminata!")
