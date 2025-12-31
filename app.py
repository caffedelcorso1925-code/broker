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
st.set_page_config(page_title="Robot Pro 52 - Fix", page_icon="💰", layout="wide")
st.title("💰 Robot Finanziario Dinamico: 52 Titoli")
st.write(f"Scansione RSI < 40 + Grafici 15gg. Ora: {datetime.now(italy_tz).strftime('%H:%M:%S')}")

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
if st.button('🚀 AVVIA SCANSIONE COMPLETA'):
    progress_bar = st.progress(0)
    
    for i, t in enumerate(titoli):
        # Scarichiamo dati (60 giorni per avere una media mobile corretta)
        df = yf.download(t, period="60d", interval="1d", progress=False)
        
        if not df.empty and len(df) > 20:
            # --- FIX PER IL TUO ERRORE (KeyError) ---
            # Appiattiamo le colonne se sono MultiIndex
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Calcolo Media Mobile 15gg
            df['Media_15'] = df['Close'].rolling(window=15).mean()
            
            # Calcolo RSI professionale
            delta = df['Close'].diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            df['RSI'] = 100 - (100 / (1 + (ema_up / ema_down)))
            
            # Dati attuali
            prezzo_attuale = float(df['Close'].iloc[-1])
            rsi_attuale = float(df['RSI'].iloc[-1])
            media_15 = float(df['Media_15'].iloc[-1])
            sconto = ((media_15 - prezzo_attuale) / media_15) * 100
            ora_segnale = datetime.now(italy_tz).strftime("%H:%M:%S")

            # --- LOGICA SEGNALE (RSI < 40) ---
            if rsi_attuale < 40:
                emoji = "🚨" if rsi_attuale < 25 else "🟢"
                
                # PULSANTE A SCOMPARSA (Expander)
                with st.expander(f"{emoji} {t} - RSI: {rsi_attuale:.1f} | Sconto: {sconto:.1f}%"):
                    st.write(f"**Prezzo attuale:** {prezzo_attuale:.2f}€ | **Media 15gg:** {media_15:.2f}€")
                    
                    # Grafico Prezzo vs Media (ultimi 15gg)
                    df_recent = df.tail(15)[['Close', 'Media_15']]
                    st.line_chart(df_recent)
                    
                    # Grafico RSI (ultimi 15gg)
                    st.write("Andamento RSI (Sotto 40 è zona acquisto):")
                    st.area_chart(df.tail(15)['RSI'])
                    
                    # Messaggio Telegram
                    msg = (f"{emoji} SEGNALE {t}\nPrezzo: {prezzo_attuale:.2f}\nRSI: {rsi_attuale:.1f}\n"
                           f"Sconto vs Media: {sconto:.1f}%\nOre: {ora_segnale}")
                    invia_telegram(msg)
            else:
                st.text(f"⚪ {t}: RSI {rsi_attuale:.1f} - Nessun segnale")
        
        progress_bar.progress((i + 1) / len(titoli))
    
    st.success("Scansione completata!")
