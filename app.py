import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# --- 1. CONFIGURAZIONE (Inserisci i tuoi dati) ---
TOKEN_BOT = "IL_TUO_TOKEN_QUI"
CHAT_ID_UTENTE = "IL_TUO_CHAT_ID_QUI"

lista_strumenti = ['AAPL', 'NVDA', 'TSLA', 'AMZN', 'MSFT', 'BTC-USD', 'ETH-USD', 'SOL-USD', 'GC=F']

def invia_telegram(messaggio):
    try:
        url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
        payload = {"chat_id": CHAT_ID_UTENTE, "text": messaggio}
        requests.post(url, data=payload)
    except:
        pass

# --- 2. INTERFACCIA ---
st.set_page_config(page_title="Robot RSI", page_icon="📈")
st.title("📈 Robot RSI Dinamico")

if st.button('🎯 Calcola RSI e Cerca Occasioni'):
    st.write("### 📊 Analisi Tecnica in corso...")
    
    for t in lista_strumenti:
        try:
            # Scarichiamo dati più lunghi (2 mesi) per calcolare bene l'RSI
            df = yf.download(t, period="2mo", interval="1d", progress=False)
            
            if not df.empty and len(df) > 14:
                # Pulizia colonne MultiIndex (la correzione di prima)
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # Calcolo RSI professionale
                chiusura = df['Close']
                delta = chiusura.diff()
                up = delta.clip(lower=0)
                down = -1 * delta.clip(upper=0)
                ema_up = up.ewm(com=13, adjust=False).mean()
                ema_down = down.ewm(com=13, adjust=False).mean()
                rs = ema_up / ema_down
                rsi = 100 - (100 / (1 + rs))
                
                rsi_attuale = float(rsi.iloc[-1])
                prezzo_attuale = float(chiusura.iloc[-1])

                # Logica Segnale (Soglia 40 per essere dinamici)
                if rsi_attuale < 40:
                    messaggio = f"✅ OCCASIONE: {t}\nPrezzo: {prezzo_attuale:.2f}\nRSI: {rsi_attuale:.1f}"
                    st.success(messaggio)
                    invia_telegram(messaggio)
                else:
                    st.info(f"⚪ {t}: Prezzo {prezzo_attuale:.2f} (RSI: {rsi_attuale:.1f})")
            else:
                st.warning(f"⚠️ {t}: Dati insufficienti per l'RSI")
                
        except Exception as e:
            st.error(f"❌ Errore su {t}")

    st.success("Analisi completata!")
