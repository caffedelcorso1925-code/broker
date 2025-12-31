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
        requests.post(url, data=payload)
    except Exception as e:
        st.error(f"Errore Telegram: {e}")

# --- CONFIGURAZIONE APP ---
st.set_page_config(page_title="Robot 52 Titoli", page_icon="📈", layout="wide")
st.title("📈 Robot Finanziario: 52 Titoli sotto Controllo")
st.write(f"Scansione attiva con soglia RSI < 40 e Grafici 15gg. Ora attuale: {datetime.now(italy_tz).strftime('%H:%M:%S')}")

# --- LISTA 52 TITOLI (Dinamici, Tech, Crypto, Italia) ---
titoli = [
    # Tecnologia & AI (USA)
    'AAPL', 'NVDA', 'TSLA', 'AMZN', 'MSFT', 'META', 'GOOGL', 'AMD', 'PLTR', 'NFLX', 
    'ARM', 'SMCI', 'AVGO', 'INTC', 'ORCL', 'SNOW', 'BABA', 'UBER', 'COIN', 'SHOP',
    # Crypto (24/7)
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'DOGE-USD', 'ADA-USD', 'XRP-USD', 'DOT-USD', 'LINK-USD',
    # Indici & Materie Prime
    'QQQ', 'SPY', 'GC=F', 'CL=F', 'SILVER',
    # Mercato Italiano (Piazza Affari)
    'RACE.MI', 'ENI.MI', 'UCG.MI', 'ISP.MI', 'STLAM.MI', 'STM.MI', 'EGP.MI', 'PST.MI', 'LDO.MI', 'G.MI',
    # Altri titoli dinamici / Meme
    'GME', 'AMC', 'PYPL', 'DIS', 'NIO', 'SQ', 'AIBOT', 'MSTR', 'MDB'
]

# --- LOGICA DI SCANSIONE ---
if st.button('🚀 Avvia Scansione Totale (52 Titoli)'):
    progress_bar = st.progress(0)
    for i, t in enumerate(titoli):
        # Scarichiamo dati sufficienti per calcolare medie e RSI (60 giorni)
        df = yf.download(t, period="60d", interval="1d", progress=False)
        
        if not df.empty and len(df) > 20:
            # Calcolo Media Mobile 15 giorni
            df['Media_15'] = df['Close'].rolling(window=15).mean()
            
            # Calcolo RSI professionale
            delta = df['Close'].diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            df['RSI'] = 100 - (100 / (1 + (ema_up / ema_down)))
            
            # Valori attuali
            prezzo_attuale = float(df['Close'].iloc[-1])
            rsi_attuale = float(df['RSI'].iloc[-1])
            media_15 = float(df['Media_15'].iloc[-1])
            sconto = ((media_15 - prezzo_attuale) / media_15) * 100
            ora_segnale = datetime.now(italy_tz).strftime("%H:%M:%S")
            
            # Logica Alert
            if rsi_attuale < 40:
                colore = "🔴" if rsi_attuale < 25 else "🟢"
                with st.expander(f"{colore} ALERT: {t} | RSI: {rsi_attuale:.1f} | Sconto: {sconto:.1f}%"):
                    st.write(f"**Prezzo:** {prezzo_attuale:.2f} | **Media 15gg:** {media_15:.2f}")
                    
                    # Grafico Prezzo vs Media
                    df_plot = df.tail(15)
                    st.line_chart(df_plot[['Close', 'Media_15']])
                    
                    # Grafico RSI
                    st.write("Andamento RSI (15 giorni):")
                    st.area_chart(df_plot['RSI'])
                    
                    # Invio Telegram
                    msg = (f"{colore} SEGNALE {t}\n"
                           f"Prezzo: {prezzo_attuale:.2f}\n"
                           f"RSI: {rsi_attuale:.1f} (Ipervenduto)\n"
                           f"Sconto vs Media 15gg: {sconto:.1f}%\n"
                           f"Ore: {ora_segnale}")
                    invia_telegram(msg)
            else:
                # Titoli non in sconto mostrati in modo compatto
                st.write(f"⚪ {t}: RSI {rsi_attuale:.1f} (Nessun segnale)")
        
        # Aggiorna barra progresso
        progress_bar.progress((i + 1) / len(titoli))

    st.success(f"Scansione di {len(titoli)} titoli completata!")
