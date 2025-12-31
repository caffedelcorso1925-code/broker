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

# --- 2. LISTA TITOLI ---
titoli = [
    'AAPL', 'NVDA', 'TSLA', 'AMZN', 'MSFT', 'META', 'GOOGL', 'AMD', 'PLTR', 'NFLX', 
    'ARM', 'SMCI', 'AVGO', 'INTC', 'ORCL', 'SNOW', 'BABA', 'UBER', 'COIN', 'SHOP',
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'DOGE-USD', 'ADA-USD', 'XRP-USD', 'DOT-USD', 'LINK-USD',
    'QQQ', 'SPY', 'GC=F', 'CL=F', 'RACE.MI', 'ENI.MI', 'UCG.MI', 'ISP.MI', 'STLAM.MI', 
    'STM.MI', 'EGP.MI', 'PST.MI', 'LDO.MI', 'G.MI', 'GME', 'AMC', 'PYPL', 'DIS', 'NIO', 
    'SQ', 'MSTR', 'MDB', 'AIBOT', 'V'
]

# --- 3. CONFIGURAZIONE APP ---
st.set_page_config(page_title="Robot Raggruppato", page_icon="🎨")
st.title("🎨 Robot Trader: Analisi per Colore")
st.write("Soglie: Compra < 35 | Vendi > 70")

# --- 4. LOGICA DI SCANSIONE ---
if st.button('🚀 AVVIA SCANSIONE RAGGRUPPATA'):
    progress_bar = st.progress(0)
    
    # Creiamo dei "cassetti" dove mettere i risultati
    compras = []
    vendis = []
    stabili = []
    
    for i, t in enumerate(titoli):
        try:
            df = yf.download(t, period="30d", interval="1d", progress=False)
            if not df.empty and len(df) > 14:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                delta = df['Close'].diff()
                up = delta.clip(lower=0)
                down = -1 * delta.clip(upper=0)
                ema_up = up.ewm(com=13, adjust=False).mean()
                ema_down = down.ewm(com=13, adjust=False).mean()
                rs = ema_up / ema_down
                rsi_attuale = float(100 - (100 / (1 + rs)).iloc[-1])
                prezzo_attuale = float(df['Close'].iloc[-1])

                testo_risultato = f"**{t}** | Prezzo: {prezzo_attuale:.2f} | RSI: {rsi_attuale:.1f}"
                
                # Mettiamo il risultato nel cassetto giusto
                if rsi_attuale < 35:
                    compras.append(testo_risultato)
                    invia_telegram(f"🟢 COMPRA: {t} (RSI {rsi_attuale:.1f})")
                elif rsi_attuale > 70:
                    vendis.append(testo_risultato)
                    invia_telegram(f"🔴 VENDI: {t} (RSI {rsi_attuale:.1f})")
                else:
                    stabili.append(f"{t}: RSI {rsi_attuale:.1f}")
        except:
            continue
        progress_bar.progress((i + 1) / len(titoli))

    # --- 5. MOSTRA I RISULTATI RAGGRUPPATI ---
    
    st.subheader("🟢 SEGNALI DI ACQUISTO (Sotto 35)")
    if compras:
        for c in compras:
            st.success(c)
    else:
        st.info("Nessun titolo da comprare al momento.")

    st.subheader("🔴 SEGNALI DI VENDITA (Sopra 70)")
    if vendis:
        for v in vendis:
            st.error(v)
    else:
        st.info("Nessun titolo da vendere al momento.")

    st.subheader("⚪ TITOLI IN FASE STABILE")
    with st.expander("Clicca per vedere i titoli stabili"):
        if stabili:
            for s in stabili:
                st.write(s)
        else:
            st.write("Nessun dato disponibile.")
