import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd

st.set_page_config(page_title="Il Mio Robot Finanziario", page_icon="📈")
st.title("💰 Il Mio Generatore di Capitale")

# Lista titoli aggiornata
titoli = ['AAPL', 'TSLA', 'NVDA', 'AMZN', 'MSFT', 'BTC-USD', 'ETH-USD']

if st.button('🤖 Avvia Scansione Ora'):
    stato = st.empty()
    
    for t in titoli:
        stato.info(f"🔍 Scaricando dati per: {t}...")
        
        # TRUCCO: Usiamo '2mo' (2 mesi) per essere sicuri di avere abbastanza giorni per l'RSI
        dati = yf.download(t, period="2mo", interval="1d", progress=False)
        
        # Controlliamo se la tabella ha dati
        if dati is not None and len(dati) > 20:
            # Calcolo RSI (usiamo i prezzi di chiusura 'Close')
            # Aggiungiamo .squeeze() per assicurarci che sia nel formato giusto
            chiusura = dati['Close'].squeeze()
            rsi_serie = ta.rsi(chiusura, length=14)
            
            if rsi_serie is not None and not rsi_serie.isna().all():
                rsi_attuale = float(rsi_serie.iloc[-1])
                prezzo_oggi = float(chiusura.iloc[-1])
                # Calcoliamo la differenza tra oggi e 5 giorni fa
                prezzo_5gg_fa = float(chiusura.iloc[-5])
                var_settimanale = ((prezzo_oggi - prezzo_5gg_fa) / prezzo_5gg_fa) * 100

                if rsi_attuale < 30 and var_settimanale < -10:
                    st.success(f"🔥 OCCASIONE SU {t}!")
                    st.write(f"Prezzo: {prezzo_oggi:.2f} | RSI: {rsi_attuale:.2f} | Calo: {var_settimanale:.2f}%")
                else:
                    st.write(f"⚪ {t}: Prezzo {prezzo_oggi:.2f} - (RSI: {rsi_attuale:.2f})")
            else:
                st.warning(f"⚠️ {t}: Problema tecnico nel calcolo RSI.")
        else:
            st.error(f"❌ {t}: Impossibile scaricare i dati. Riprova tra poco.")
            
    stato.success("✅ Scansione completata!")
