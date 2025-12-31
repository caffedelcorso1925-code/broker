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

# --- 2. CONFIGURAZIONE APP ---
st.set_page_config(page_title="Robot 52 Trader", page_icon="📈")
st.title("📈 Robot 52 Titoli - Strategia RSI")
st.write(f"Soglie: <35 COMPRA (Verde) | >70 VENDI (Rosso). Ora: {datetime.now(italy_tz).strftime('%H:%M:%S')}")

# --- 3. LISTA 52 TITOLI (Sempre visibile per evitare NameError) ---
titoli = [
    'AAPL', 'NVDA', 'TSLA', 'AMZN', 'MSFT', 'META', 'GOOGL', 'AMD', 'PLTR', 'NFLX', 
    'ARM', 'SMCI', 'AVGO', 'INTC', 'ORCL', 'SNOW', 'BABA', 'UBER', 'COIN', 'SHOP',
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'DOGE-USD', 'ADA-USD', 'XRP-USD', 'DOT-USD', 'LINK-USD',
    'QQQ', 'SPY', 'GC=F', 'CL=F', 'RACE.MI', 'ENI.MI', 'UCG.MI', 'ISP.MI', 'STLAM.MI', 
    'STM.MI', 'EGP.MI', 'PST.MI', 'LDO.MI', 'G.MI', 'GME', 'AMC', 'PYPL', 'DIS', 'NIO', 
    'SQ', 'MSTR', 'MDB', 'AIBOT', 'V'
]

# --- 4. LOGICA DI SCANSIONE ---
if st.button('🚀 AVVIA SCANSIONE PROFESSIONALE'):
    progress_bar = st.progress(0)
    segnali_buy = 0
    segnali_sell = 0
    
    for i, t in enumerate(titoli):
        try:
            # Scarichiamo dati (30 giorni bastano per l'RSI)
            df = yf.download(t, period="30d", interval="1d", progress=False)
            
            if not df.empty and len(df) > 14:
                # Fix per colonne Yahoo Finance (MultiIndex)
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # Calcolo RSI professionale
                delta = df['Close'].diff()
                up = delta.clip(lower=0)
                down = -1 * delta.clip(upper=0)
                ema_up = up.ewm(com=13, adjust=False).mean()
                ema_down = down.ewm(com=13, adjust=False).mean()
                rs = ema_up / ema_down
                rsi_attuale = float(100 - (100 / (1 + rs)).iloc[-1])
                prezzo_attuale = float(df['Close'].iloc[-1])
                ora_segnale = datetime.now(italy_tz).strftime("%H:%M:%S")

                # --- LOGICA SEGNALI ---
                
                # 🟢 COMPRARE (Sotto 35)
                if rsi_attuale < 35:
                    segnali_buy += 1
                    msg = f"🟢 COMPRA: {t} | Prezzo: {prezzo_attuale:.2f} | RSI: {rsi_attuale:.1f}"
                    st.success(msg)
                    invia_telegram(f"🚀 SEGNALE COMPRA\n{msg}\nOre: {ora_segnale}")
                
                # 🔴 VENDERE (Sopra 70)
                elif rsi_attuale > 70:
                    segnali_sell += 1
                    msg = f"🔴 VENDERE: {t} | Prezzo: {prezzo_attuale:.2f} | RSI: {rsi_attuale:.1f}"
                    st.error(msg)
                    invia_telegram(f"💰 SEGNALE VENDI\n{msg}\nOre: {ora_segnale}")
                
                # ⚪ STABILE (Tra 35 e 70)
                else:
                    st.text(f"⚪ {t}: RSI {rsi_attuale:.1f} - Stabile")
                    
        except Exception as e:
            st.error(f"Errore su {t}: {e}")
        
        # Avanzamento barra
        progress_bar.progress((i + 1) / len(titoli))
    
    st.success(f"Scansione completata! Trovati {segnali_buy} segnali Buy e {segnali_sell} segnali Sell.")
