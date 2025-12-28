import streamlit as st
import yfinance as yf
import pandas_ta as ta

# 1. Impostazioni della pagina (Titolo che vedi nel browser)
st.set_page_config(page_title="Il Mio Robot Finanziario", page_icon="📈")

# 2. Titolo dell'App
st.title("💰 Il Mio Generatore di Capitale")
st.write("Questo robot analizza il mercato per trovare affari con i tuoi 10€.")

# 3. Lista delle cose da controllare (puoi aggiungerne altre tra virgolette)
# Esempio: 'AAPL' è Apple, 'TSLA' è Tesla, 'BTC-USD' è Bitcoin
titoli = ['AAPL', 'TSLA', 'NVDA', 'AMZN', 'MSFT', 'BTC-USD', 'ETH-USD']

# 4. Creazione del Bottone
if st.button('🤖 Avvia Scansione Ora'):
    st.write("Sto controllando i prezzi... attendi un attimo.")
    
    # Questo ciclo controlla ogni titolo della lista uno per uno
    for t in titoli:
        # Scarichiamo i dati dell'ultimo mese
        dati = yf.download(t, period="1mo", interval="1d")
        
        if not dati.empty:
            # Calcoliamo l'RSI (l'indicatore della "paura" del mercato)
            dati['RSI'] = ta.rsi(dati['Close'], length=14)
            
            # Calcoliamo quanto è sceso il prezzo negli ultimi 5 giorni
            var_settimanale = ((dati['Close'].iloc[-1] - dati['Close'].iloc[-5]) / dati['Close'].iloc[-5]) * 100
            
            prezzo_attuale = dati['Close'].iloc[-1]
            rsi_attuale = dati['RSI'].iloc[-1]

            # --- LOGICA DEL ROBOT ---
            # SE l'RSI è sotto 30 (tutti hanno venduto troppo) 
            # E il prezzo è sceso più del 10%...
            if rsi_attuale < 30 and var_settimanale < -10:
                st.success(f"🔥 OCCASIONE SU {t}!")
                st.write(f"Il prezzo è {prezzo_attuale:.2f}€. È sceso del {var_settimanale:.2f}% in una settimana.")
                st.write(f"L'indicatore RSI è a {rsi_attuale:.2f}: il mercato è in svendita!")
                st.write("---")
            else:
                # Se non è un affare, il robot ci dice che è tutto normale
                st.info(f"{t}: Nessuna occasione interessante oggi (RSI: {rsi_attuale:.2f})")
