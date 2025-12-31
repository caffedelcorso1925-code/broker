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

# --- 2. LISTA TITOLI (Sempre definita all'inizio) ---
titoli = [
    'AAPL', 'NVDA', 'TSLA', 'AMZN', 'MSFT', 'META', 'GOOGL', 'AMD', 'PLTR', 'NFLX', 
    'ARM', 'SMCI', 'AVGO', 'INTC', 'ORCL', 'SNOW', 'BABA', 'UBER', 'COIN', 'SHOP',
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'DOGE-USD', 'ADA-USD', 'XRP-USD', 'DOT-USD', 'LINK-USD',
    'QQQ', 'SPY', 'GC=F', 'CL=F', 'RACE.MI', 'ENI.MI', 'UCG.MI', 'ISP.MI', 'STLAM.MI', 
    'STM.MI', 'EGP.MI', 'PST.MI', 'LDO.MI', 'G.MI', 'GME', 'AMC', 'PYPL', 'DIS', 'NIO', 
    'SQ', 'MSTR', 'MDB', 'AIBOT', 'V'
]

# --- 3. CONFIGURAZIONE APP ---
st.set_page_config(page_title="Robot 52 Raggruppato", page_icon="🎯")
st.title("🎯 Robot Trader: Risultati per Colore")
st.write(f"Soglie: Compra < 35 | Vendi > 70")

# --- 4. LOGICA DI SCANSIONE ---
if st.button('🚀 AVVIA SCANSIONE E RAGGRUPPA'):
    progress_bar = st.progress(0)
    
    # Cassetti per raggruppare i titoli
    lista_verde = []
    lista_rossa = []
    lista_bianca = []
    
    for i, t in enumerate(titoli):
        try:
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

                testo = f"**{t}** | Prezzo: {prezzo_attuale:.2f} | RSI: {rsi_attuale:.1f}"
                
                # Smistamento nei cassetti
                if rsi_attuale < 35:
                    lista_verde.append(testo)
                    invia_telegram(f"🟢 COMPRA: {t} (RSI {rsi_attuale:.1f})")
                elif rsi_attuale > 70:
                    lista_rossa.append(testo)
                    invia_telegram(f"🔴 VENDI: {t} (RSI {rsi_attuale:.1f})")
                else:
                    lista_bianca.append(f"{t}: RSI {rsi_attuale:.1f}")
        except:
            continue
        
        progress_bar.progress((i + 1) / len(titoli))

    # --- 5. VISUALIZZAZIONE FINALE RAGGRUPPATA ---
    
    st.divider()
    
    # 🟢 BLOCCO VERDE
    st.header("🟢 SEGNALI DI ACQUISTO")
    if lista_verde:
        for segnale in lista_verde:
            st.success(segnale)
    else:
        st.write("Nessun titolo sotto RSI 35.")

    # 🔴 BLOCCO ROSSO
    st.header("🔴 SEGNALI DI VENDITA")
    if lista_rossa:
        for segnale in lista_rossa:
            st.error(segnale)
    else:
        st.write("Nessun titolo sopra RSI 70.")

    # ⚪ BLOCCO BIANCO (A scomparsa per non ingombrare)
    st.header("⚪ TITOLI STABILI")
    with st.expander("Clicca per vedere i titoli in zona neutra"):
        if lista_bianca:
            for segnale in lista_bianca:
                st.text(segnale)
        else:
            st.write("Nessun dato.")

    st.balloons() # Festeggia la fine della scansione!
