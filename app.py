import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- CONFIGURAZIONE ---
TOKEN_BOT = "IL_TUO_TOKEN_QUI"
CHAT_ID_UTENTE = "IL_TUO_CHAT_ID_QUI"

lista_strumenti = ['AAPL', 'NVDA', 'TSLA', 'AMZN', 'MSFT', 'BTC-USD', 'ETH-USD', 'SOL-USD', 'GC=F', 'RACE.MI']

def invia_telegram(messaggio):
    try:
        url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
        payload = {"chat_id": CHAT_ID_UTENTE, "text": messaggio}
        requests.post(url, data=payload)
    except:
        pass

st.set_page_config(page_title="Robot RSI Pro", page_icon="📊")
st.title("📊 Monitoraggio RSI Dinamico")

if st.button('🚀 AVVIA SCANSIONE MERCATI'):
    st.write("### 🔎 Analisi in tempo reale")
    
    for t in lista_strumenti:
        try:
            # Scarichiamo dati (2 mesi per avere un RSI preciso)
            df = yf.download(t, period="2mo", interval="1d", progress=False)
            
            if not df.empty and len(df) > 14:
                # Correzione colonne
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # CALCOLO RSI
                chiusura = df['Close'].astype(float)
                delta = chiusura.diff()
                up = delta.clip(lower=0)
                down = -1 * delta.clip(upper=0)
                ema_up = up.ewm(com=13, adjust=False).mean()
                ema_down = down.ewm(com=13, adjust=False).mean()
                rs = ema_up / ema_down
                rsi_serie = 100 - (100 / (1 + rs))
                
                rsi_attuale = round(float(rsi_serie.iloc[-1]), 2)
                prezzo = round(float(chiusura.iloc[-1]), 2)

                # --- LOGICA COLORI (Bottoni/Box Visivi) ---
                if rsi_attuale < 35:
                    # VERDE: Super Sottocosto
                    st.success(f"🟩 **COMPRA (Oversold)** | {t} | Prezzo: {prezzo} | **RSI: {rsi_attuale}**")
                    invia_telegram(f"🟢 SEGNALE ACQUISTO: {t}\nPrezzo: {prezzo}\nRSI: {rsi_attuale}")
                
                elif 35 <= rsi_attuale < 45:
                    # BIANCO/GRIGIO: Interessante
                    st.write(f"⬜ **ATTENZIONE** | {t} | Prezzo: {prezzo} | **RSI: {rsi_attuale}**")
                
                elif rsi_attuale > 70:
                    # ROSSO: Troppo caro
                    st.error(f"🟥 **VENDI (Overbought)** | {t} | Prezzo: {prezzo} | **RSI: {rsi_attuale}**")
                
                else:
                    # NEUTRO
                    st.info(f"🔵 **NEUTRO** | {t} | Prezzo: {prezzo} | **RSI: {rsi_attuale}**")
            else:
                st.warning(f"⚠️ {t}: Dati non sufficienti.")
                
        except Exception as e:
            st.error(f"❌ Errore su {t}")

    st.success("Scansione completata!")
