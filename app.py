import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd

st.set_page_config(page_title="Il Mio Robot Finanziario", page_icon="📈")
st.title("💰 Il Mio Generatore di Capitale")
st.write("Clicca il tasto sotto per iniziare l'analisi.")

titoli = ['AAPL', 'TSLA', 'NVDA', 'AMZN', 'MSFT', 'BTC-USD', 'ETH-USD']

if st.button('🤖 Avvia Scansione Ora'):
    # Creiamo uno spazio vuoto per i messaggi di stato
    stato = st.empty()
    
    for t in titoli:
        stato.info(f"🔍 Analisi in corso: {t}...")
        
        # Scarichiamo i dati
        dati = yf.download(t, period="1mo", interval="1d", progress=False)
        
        if not dati.empty and len(dati) >= 14:
            rsi_serie = ta.rsi(dati['Close'], length=14)
            
            if rsi_serie is not None and not rsi_serie.empty:
                rsi_attuale = float(rsi_serie.iloc[-1])
                # Calcolo variazione ultimi 5 giorni
                prezzo_oggi = float(dati['Close'].iloc[-1])
                prezzo_5gg_fa = float(dati['Close'].iloc[-5])
                var_settimanale = ((prezzo_oggi - prezzo_5gg_fa) / prezzo_5gg_fa) * 100

                # MOSTRA SEMPRE IL RISULTATO PER SAPERE CHE FUNZIONA
                if rsi_attuale < 30 and var_settimanale < -10:
                    st.success(f"🔥 OCCASIONE SU {t}!")
                    st.write(f"Prezzo: {prezzo_oggi:.2f} | RSI: {rsi_attuale:.2f} | Calo: {var_settimanale:.2f}%")
                else:
                    st.write(f"⚪ {t}: Prezzo {prezzo_oggi:.2f} - Nessun segnale (RSI: {rsi_attuale:.2f})")
            else:
                st.warning(f"⚠️ {t}: Calcolo RSI fallito.")
        else:
            st.warning(f"⚠️ {t}: Dati non trovati o insufficienti.")
    
    stato.success("✅ Scansione completata!")
