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

# --- 2. DEFINIZIONE LISTA TITOLI ---
titoli = [
    'AAPL', 'NVDA', 'TSLA', 'AMZN', 'MSFT', 'META', 'GOOGL', 'AMD', 'PLTR', 'NFLX', 
    'ARM', 'SMCI', 'AVGO', 'INTC', 'ORCL', 'SNOW', 'BABA', 'UBER', 'COIN', 'SHOP',
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'DOGE-USD', 'ADA-USD', 'XRP-USD', 'DOT-USD', 'LINK-USD',
    'QQQ', 'SPY', 'GC=F', 'CL=F', 'RACE.MI', 'ENI.MI', 'UCG.MI', 'ISP.MI', 'STLAM.MI', 
    'STM.MI', 'EGP.MI', 'PST.MI', 'LDO.MI', 'G.MI', 'GME', 'AMC', 'PYPL', 'DIS', 'NIO', 
    'SQ', 'MSTR', 'MDB', 'AIBOT', 'V'
]

# --- 3. CONFIGURAZIONE APP ---
st.set_page_config(page_title="Robot 52 Grouped", page_icon="📊")
st.title("📊 Robot Trader: Risultati Raggruppati")
st.write(f"Strategia: Compra < 35 | Vendi > 70")

# --- 4. LOGICA DI SCANSIONE ---
if st.button('🚀 AVVIA SCANSIONE RAGGRUPPATA'):
    progress_bar = st.progress(0)
    
    # Liste per raggruppare i risultati
    lista_compra = []
    lista_vendi = []
    lista_stabili = []
    
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

                info = f"**{t}** - RSI: {rsi_attuale:.1f} | Prezzo: {prezzo_attuale:.2f}"
                
                if rsi_attuale < 35:
                    lista_compra.append(info)
                    invia_telegram(f"🟢 COMPRA: {t} (RSI {rsi_attuale:.1f})")
                elif rsi_attuale > 70:
                    lista_vendi.append(info)
                    invia_telegram(f"🔴 VENDI: {t} (RSI {rsi_attuale:.1f})")
                else:
                    lista_stabili.append(f"{t}: RSI {rsi_attuale:.1f}")
        except:
            continue
        progress_bar.progress((i + 1) / len(titoli))

    # --- 5. VISUALIZZAZIONE RAGGRUPPATA ---
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🟢 DA COMPRARE (<35)")
        if lista_compra:
            for item in lista_compra:
                st.success(item)
        else:
            st.write("Nessun titolo in sconto.")

    with col2:
        st.subheader("🔴 DA VENDERE (>70)")
        if lista_vendi:
            for item in lista_vendi:
                st.error(item)
        else:
            st.write("Nessun titolo in ipercomprato.")

    st.divider()
    
    with st.expander("⚪ TITOLI STABILI"):
        if lista_stabili:
            for item in lista_stabili:
                st.write(item)
