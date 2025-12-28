import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd

st.set_page_config(page_title="Il Mio Robot Finanziario", page_icon="📈")
st.title("💰 Il Mio Generatore di Capitale")
st.write("Analisi in corso per i tuoi 10€...")

titoli = ['AAPL', 'TSLA', 'NVDA', 'AMZN', 'MSFT', 'BTC-USD', 'ETH-USD']

if st.button('🤖 Avvia Scansione Ora'):
    for t in titoli:
        dati = yf.download(t, period="1mo", interval="1d")
        
        if not dati.empty and len(dati) > 14:
            # Calcolo RSI
            rsi_serie = ta.rsi(dati['Close'], length=14)
            
            # Controlliamo che ci siano abbastanza dati per l'RSI
            if rsi_serie is not None and not rsi_serie.empty:
                rsi_attuale = rsi_serie.iloc[-1]
                var_settimanale = ((dati['Close'].iloc[-1] - dati['Close'].iloc[-5]) / dati['Close'].iloc[-5]) * 100
                prezzo_attuale = dati['Close'].iloc[-1]

                # CONTROLLO DI SICUREZZA: verifichiamo che rsi_attuale sia un numero reale
                if pd.notnull(rsi_attuale):
                    if rsi_attuale < 30 and var_settimanale < -10:
                        st.success(f"🔥 OCCASIONE SU {t}!")
                        st.write(f"Prezzo: {prezzo_attuale:.2f}€ | RSI: {rsi_attuale:.2f} | Calo: {var_settimanale:.2f}%")
                    else:
                        st.info(f"{t}: Tutto normale (RSI: {rsi_attuale:.2f})")
                else:
                    st.warning(f"{t}: Dati RSI non disponibili al momento.")
        else:
            st.warning(f"{t}: Non ci sono abbastanza dati storici.")
