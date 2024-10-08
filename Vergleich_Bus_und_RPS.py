import streamlit as st
from datetime import date
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import toml

st.set_page_config(page_title="OekoRPS")

# Custom CSS to hide the + and - buttons
hide_buttons_css = """
    <style>
    .stNumberInput button.step-up, .stNumberInput button.step-down {
        display: none;
    }
    </style>
"""
# Inject the custom CSS into the Streamlit app
st.markdown(hide_buttons_css, unsafe_allow_html=True)

# Setze das Thema aus der config.toml Datei
config = toml.load(".streamlit/config.toml")

# Funktion zur Anzeige der Sidebar
def show_sidebar():
    st.sidebar.image("Logo_of_Fachhochschule_Münster.png", use_column_width=True)
    st.sidebar.markdown("""
        <style>
            .css-18e3th9 {  
                width: 50x;  
                position: fixed;
                right: 0;
                top: 0;
                height: 100%;
                margin-top: 0;
            }
            .css-1l02zno {  
                margin-left: auto;
            }
        </style>
    """, unsafe_allow_html=True)

################################################################ Berechnung RPS ################################################################


def show_methodik():
    with st.expander("**Methodik**"):
        st.write("Das Programm dient zur Bestimmung der CO2eq-Emissionen von Ridepooling-Systemen im Vergleich zu konventionellen Bussystemen. Ziel ist es, die CO2eq-Emissionen pro Personenkilometer (g CO2eq/Pkm) zu berechnen und diese gegenüberzustellen. Dabei wird auch der CO2eq-Ausstoß des Busses anhand seiner Platzausnutzung berechnet und dem des Ridepooling-Systems gegenübergestellt. Diese Auswertung ist besonders sinnvoll, um die ökologische Nachhaltigkeit verschiedener Verkehrssysteme fundiert zu bewerten. Durch den Vergleich der CO2eq-Emissionen beider Systeme kann aufgezeigt werden, wie effizient sie in Bezug auf Platzausnutzung und Emissionsvermeidung sind. Dies hilft, Potenziale zur Reduzierung von Emissionen durch optimierte Platzausnutzung oder alternative Mobilitätskonzepte zu identifizieren und somit fundierte Entscheidungen für eine umweltfreundlichere Mobilität zu treffen.")
        
        st.write("**Methodische Vorgehensweise:**")

        st.write("""
        - **Datenerhebung und Eingabe:** Der Benutzer gibt grundlegende Informationen zum Ridepooling-System, wie Betriebsdaten (Anzahl der Fahrten, transportierte Fahrgäste) und Fahrzeugflottendaten (Verbrauchsdaten, gefahrene Kilometer) ein.

        - **Berechnung der Umweltwirkungen:** Basierend auf den Eingabedaten werden die Gesamtemissionen (Benzin, Diesel, Strom) des Ridepooling-Systems berechnet. Die Emissionen pro Personenkilometer werden ermittelt.

        - **Vergleich mit Bussystem:** Das Programm berechnet die durchschnittliche Platzausnutzung eines Busses und den entsprechenden CO2eq-Ausstoß pro Personenkilometer, angepasst an unterschiedliche Platzausnutzungen. Diese Werte werden mit denen des Ridepooling-Systems verglichen.

        """)


# Funktion zur Initialisierung der Session State Variablen
def initialize_session_state():
    if 'vehicle_list' not in st.session_state:
        st.session_state['vehicle_list'] = []

# Funktion zur Validierung der Eingaben
def validate_input(text):
    return text.isdigit()

def validate_input_int(text):
    try:
        value = int(text)
        return 0 <= value <= 100
    except ValueError:
        return False

# Funktion zur Darstellung der Allgemeinen Informationen
# Funktion zur Darstellung der Allgemeinen Informationen
def show_general_info():
    with st.expander("**1.1 Allgemeine Informationen**"):
        st.info("**Hinweis:** Bitte geben Sie zunächst allgemeine Informationen zum Ridepooling-System an. Bitte berücksichtigen Sie den Betrachtungszeitraum, auf welchen sich die folgenden Angaben beziehen.")
        name_ridepooling_system = st.text_input("Name des Ridepooling-Systems:")
        start_date = st.date_input("Beginn Betrachtungszeitraum:", date(2022, 1, 1))
        end_date = st.date_input("Ende Betrachtungszeitraum:", date(2022, 12, 31))

        st.session_state.update({
            'name_ridepooling_system': name_ridepooling_system,
            'start_date': start_date,
            'end_date': end_date
        })
        # Das Startdatum muss vor dem Enddatum liegen
        if start_date > end_date:
            st.error("Das Startdatum muss vor dem Enddatum liegen.")
        # Weder Start-Datum noch End-Datum dürfen in der Zukunft liegen
        elif end_date > date.today():
            st.error("Das Enddatum darf nicht in der Zukunft liegen.")
        else:
            st.session_state.update({
                'name_ridepooling_system': name_ridepooling_system,
                'start_date': start_date,
                'end_date': end_date
            })
    


# Funktion zur Darstellung der Systemleistungs-Sektion
def show_system_performance():
    with st.expander("**1.2 Beförderungsleistung**"):
        st.info("**Hinweis:** Bitte geben Sie die Beförderungsleistung des Ridepooling-Systems an. Hierzu zählen die Anzahl der abgeschlossenen Buchungen und die Anzahl der transportierten Fahrgäste im Betrachtungszeitraum. Optional können Sie auch ein Ridepooling-System auswählen, um vorausgefüllte Daten zu erhalten.")
        
        # Daten für das Dropdown-Menü
        ridepooling_data = {
            "Eigene Angaben": {"Fahrten": 0, "Transportierte Fahrgäste": 0},
            "bussi": {"Fahrten": 8450, "Transportierte Fahrgäste": 13839, "vehicle_type": "LEVC TX (Volvo XC 90 Recharge T8 AWD)", "Benzinverbrauch (l/100km)": 1.2, "Dieselverbrauch (l/100km)": 0.0, "Stromverbrauch (kWh/100km)": 20.5, "Kilometer leer": 50422.31, "Kilometer besetzt": 40063.44},
            "G-Mobil": {"Fahrten": 60045, "Transportierte Fahrgäste": 74556},
            "kommit-Shuttle": {"Fahrten": 21895, "Transportierte Fahrgäste": 26263},
            "LOOPmünster": {"Fahrten": 151415, "Transportierte Fahrgäste": 187309},
        }

        # Dropdown-Menü zum Auswählen des Ridepooling-Systems
        selected_system = st.selectbox('Wählen Sie ein Ridepooling-System (Optional):', list(ridepooling_data.keys()))

        # Eingabefelder mit vorausgefüllten Daten basierend auf der Auswahl
        abgeschlossene_buchungen = st.number_input("Abgeschlossene Buchungen im Betrachtungszeitraum:", value=ridepooling_data[selected_system]["Fahrten"], min_value=0, step=0)
        transportierte_fahrgaeste = st.number_input("Transportierte Fahrgäste im Betrachtungszeitraum:", value=ridepooling_data[selected_system]["Transportierte Fahrgäste"], min_value=0, step=0)

        # Speichern der globalen Variablen
        st.session_state.update({
            'abgeschlossene_buchungen': abgeschlossene_buchungen,
            'transportierte_fahrgaeste': transportierte_fahrgaeste
        })

# Funktion zur Darstellung der Fahrzeugflotten- und Fahrtleistungs-Sektion
def show_vehicle_fleet_performance():
    with st.expander("**1.3 Fahrzeugflotte & Fahrtleistung**"):
        # Vordefinierte Fahrzeugtypen und deren Verbrauchsdaten
        vehicle_types = {
            "LEVC TX (Volvo XC 90 Recharge T8 AWD)": {"Benzinverbrauch (l/100km)": 1.2, "Dieselverbrauch (l/100km)": 0.0, "Stromverbrauch (kWh/100km)": 20.5, "Kilometer leer": 0, "Kilometer besetzt": 0},
            "Mercedes Vito lang 114 CDI": {"Benzinverbrauch (l/100km)": 0.0, "Dieselverbrauch (l/100km)": 8.4, "Stromverbrauch (kWh/100km)": 0.0, "Kilometer leer": 0, "Kilometer besetzt": 0},
            "Mercedes eVito Tourer PRO lang (90 kWh)": {"Benzinverbrauch (l/100km)": 0.0, "Dieselverbrauch (l/100km)": 0.0, "Stromverbrauch (kWh/100km)": 29.8, "Kilometer leer": 0, "Kilometer besetzt": 0},
            "Anderer Fahrzeugtyp": {"Benzinverbrauch (l/100km)": 0.0, "Dieselverbrauch (l/100km)": 0.0, "Stromverbrauch (kWh/100km)": 0.0, "Kilometer leer": 0, "Kilometer besetzt": 0}
        }

        # Initialisierung der Fahrzeugliste im Session State, falls noch nicht vorhanden
        if 'vehicle_list' not in st.session_state:
            st.session_state['vehicle_list'] = []

        # Fahrzeugdaten durch Nutzereingaben modifizieren
        with st.container():
            st.info("**Hinweis:** Bitte geben Sie an, welche Fahrzeugtypen in Ihrer Flotte vorhanden sind. Bitte geben Sie für jeden Fahrzeugtyp die gefahrenen Kilometerleistungen (leer, besetzt) flottenbezogen an. Bitte beziehen Sie sich auf den Betrachtungszeitraum. Die vorgegebenen Verbrauchsdaten beziehen sich auf die WLTP-Methode (Deutsche Automobil Treuhand GmbH, Leitfaden CO2eq (2022)). Passen Sie ggf. Verbrauchsdaten an. Klicken Sie anschließend auf 'Daten übernehmen & berechnen'. Sie können andere Fahrzeugtypen abbilden, indem Sie ein leeres Feld auswählen und die entsprechenden Kilometer- & Verbrauchsdaten eingeben.")

        with st.form("vehicle_form", clear_on_submit=True):
            new_vehicle_type = st.selectbox("Wählen Sie einen Fahrzeugtyp", list(vehicle_types.keys()))
            add_vehicle = st.form_submit_button("Fahrzeug hinzufügen")
        if add_vehicle:
            data = vehicle_types[new_vehicle_type].copy() if new_vehicle_type in vehicle_types else {"Benzinverbrauch (l/100km)": 0.0, "Dieselverbrauch (l/100km)": 0.0, "Stromverbrauch (kWh/100km)": 0.0, "Kilometer leer": 0, "Kilometer besetzt": 0}
            data['Fahrzeugtyp'] = new_vehicle_type  # Füge den Fahrzeugtyp hinzu
            vehicle_id = len(st.session_state['vehicle_list']) + 1
            st.session_state[f'vehicle_{vehicle_id}'] = data
            st.session_state['vehicle_list'].append(data)

        for i, vehicle in enumerate(st.session_state['vehicle_list'], start=1):
            cols = st.columns((3, 1, 1, 1, 1, 1))
            vehicle['Fahrzeugtyp'] = cols[0].text_input(f"Fahrzeugtyp {i}", vehicle['Fahrzeugtyp'])
            vehicle['Benzinverbrauch (l/100km)'] = cols[1].number_input(f"Benzin {i} (l/100km)", value=vehicle['Benzinverbrauch (l/100km)'], min_value=0.0, format='%f')
            vehicle['Dieselverbrauch (l/100km)'] = cols[2].number_input(f"Diesel {i} (l/100km)", value=vehicle['Dieselverbrauch (l/100km)'], min_value=0.0, format='%f')
            vehicle['Stromverbrauch (kWh/100km)'] = cols[3].number_input(f"Strom {i} (kWh/100km)", value=vehicle['Stromverbrauch (kWh/100km)'], min_value=0.0, format='%f')
            vehicle['Kilometer leer'] = cols[4].number_input(f"KM leer {i}", value=vehicle['Kilometer leer'], min_value=0, format='%d')
            vehicle['Kilometer besetzt'] = cols[5].number_input(f"KM besetzt {i}", value=vehicle['Kilometer besetzt'], min_value=0, format='%d')
            # Speichern der globalen Variablen
            st.session_state['Benzinverbrauch (l/100km)'] = vehicle['Benzinverbrauch (l/100km)'],
            st.session_state['Dieselverbrauch (l/100km)'] = vehicle['Dieselverbrauch (l/100km)'],
            st.session_state['Stromverbrauch (kWh/100km)'] = vehicle['Stromverbrauch (kWh/100km)']

        if st.button('Letztes Fahrzeug entfernen'):
            if st.session_state['vehicle_list']:
                removed_vehicle_id = len(st.session_state['vehicle_list'])
                st.session_state.pop(f'vehicle_{removed_vehicle_id}', None)  # Remove the global variable
                st.session_state['vehicle_list'].pop()

        # Berechne die Kilometer leer und besetzt für die gesamte Flotte
        fahrzeugkilometer_leer = sum(vehicle['Kilometer leer'] for vehicle in st.session_state['vehicle_list'])
        fahrzeugkilometer_besetzt = sum(vehicle['Kilometer besetzt'] for vehicle in st.session_state['vehicle_list'])

        if st.button('Daten übernehmen & berechnen'):
            try:
                abgeschlossene_buchungen = float(st.session_state['abgeschlossene_buchungen'])
                transportierte_fahrgaeste = float(st.session_state['transportierte_fahrgaeste'])
                fahrzeugkilometer_leer = float(fahrzeugkilometer_leer)
                fahrzeugkilometer_besetzt = float(fahrzeugkilometer_besetzt)
                fahrzeugkilometer_gesamt = round(fahrzeugkilometer_leer + fahrzeugkilometer_besetzt, 2)
                durchschnittliche_fahrtdistanz_mit_lk = round(fahrzeugkilometer_gesamt / abgeschlossene_buchungen, 2) if abgeschlossene_buchungen > 0 else 0
                durchschnittliche_fahrtdistanz_mit_bk = round(fahrzeugkilometer_besetzt / abgeschlossene_buchungen, 2) if abgeschlossene_buchungen > 0 else 0
                personenkilometer_gefahren = round((fahrzeugkilometer_besetzt / abgeschlossene_buchungen) * transportierte_fahrgaeste, 2) if abgeschlossene_buchungen > 0 else 0

                # Berechnungen der neuen Kennzahlen
                leerkilometeranteil = round((fahrzeugkilometer_leer / fahrzeugkilometer_gesamt) *100, 2) if fahrzeugkilometer_gesamt > 0 else 0
                buendelungsquote = round(personenkilometer_gefahren / fahrzeugkilometer_gesamt, 2) if fahrzeugkilometer_gesamt > 0 else 0
                besetzungsquote = round(personenkilometer_gefahren / fahrzeugkilometer_besetzt, 2) if fahrzeugkilometer_besetzt > 0 else 0

                # Speichern des Werts in den Sitzungszustand
                st.session_state.update({
                    'fahrzeugkilometer_leer': fahrzeugkilometer_leer,
                    'fahrzeugkilometer_besetzt': fahrzeugkilometer_besetzt,
                    'fahrzeugkilometer_gesamt': fahrzeugkilometer_gesamt,
                    'durchschnittliche_fahrtdistanz_mit_lk': durchschnittliche_fahrtdistanz_mit_lk,
                    'durchschnittliche_fahrtdistanz_mit_bk': durchschnittliche_fahrtdistanz_mit_bk,
                    'personenkilometer_gefahren': personenkilometer_gefahren,
                    'leerkilometeranteil': leerkilometeranteil,
                    'buendelungsquote': buendelungsquote,
                    'besetzungsquote': besetzungsquote,

                })

                benzinverbrauch_gesamt = sum(vehicle['Benzinverbrauch (l/100km)'] * ((vehicle['Kilometer besetzt'] + vehicle['Kilometer leer']) / 100) for vehicle in st.session_state['vehicle_list'])
                dieselverbrauch_gesamt = sum(vehicle['Dieselverbrauch (l/100km)'] * ((vehicle['Kilometer besetzt'] + vehicle['Kilometer leer']) / 100) for vehicle in st.session_state['vehicle_list'])
                stromverbrauch_gesamt = sum(vehicle['Stromverbrauch (kWh/100km)'] * ((vehicle['Kilometer besetzt'] + vehicle['Kilometer leer']) / 100) for vehicle in st.session_state['vehicle_list'])

                with st.container():
                    
                    st.write("**Fahrzeugleistung und -nutzung**")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("Kilometer (leer):")
                    with col2:
                        st.write(f"{fahrzeugkilometer_leer} km")

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("Kilometer (besetzt):")
                    with col2:
                        st.write(f"{fahrzeugkilometer_besetzt} km")

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("Fahrzeugkilometer (gesamt):")
                    with col2:
                        st.write(f"{fahrzeugkilometer_gesamt} km")

                    st.write("**Durchschnittliche Fahrtdistanzen**")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("Durchschnittliche Fahrtdistanz je Buchung (einschl. Leerkilometer):")
                    with col2:
                        st.write(f"{durchschnittliche_fahrtdistanz_mit_lk} km")

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("Durchschnittliche Fahrtdistanz je Buchung (mit Fahrgast):")
                    with col2:
                        st.write(f"{durchschnittliche_fahrtdistanz_mit_bk} km")

                    st.write("**Personenkilometer**")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("Personenkilometer (gefahren):")
                    with col2:
                        st.write(f"{personenkilometer_gefahren} km")

                    st.write("**Leistungs-Kennzahlen**")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("Leerkilometeranteil:")
                    with col2:
                        st.write(f"{leerkilometeranteil} %")

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("Bündelungsquote (nach § 50 Absatz 3 PBefG):")
                    with col2:
                        st.write(f"{buendelungsquote:.2f}")

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("Besetzungsquote (nach H Kripoo, 2021)")
                    with col2:
                        st.write(f"{besetzungsquote}")

                    st.write("**Verbrauchsdaten Fahrzeugflotte**")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("Benzinverbrauch des Ridepooling-Systems:")
                    with col2:
                        st.write(f"{benzinverbrauch_gesamt:.2f} l")

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("Dieselverbrauch des Ridepooling-Systems:")
                    with col2:
                        st.write(f"{dieselverbrauch_gesamt:.2f} l")

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("Stromverbrauch des Ridepooling-Systems:")
                    with col2:
                        st.write(f"{stromverbrauch_gesamt:.2f} kWh")

                # Save the total consumptions to the session state
                st.session_state.update({
                    'benzinverbrauch_gesamt': benzinverbrauch_gesamt,
                    'dieselverbrauch_gesamt': dieselverbrauch_gesamt,
                    'stromverbrauch_gesamt': stromverbrauch_gesamt
                })

                # Speichern der berechneten Werte im Sitzungszustand
                st.session_state.update({
                    'fahrzeugkilometer_leer': fahrzeugkilometer_leer,
                    'fahrzeugkilometer_besetzt': fahrzeugkilometer_besetzt,
                    'fahrzeugkilometer_gesamt': fahrzeugkilometer_gesamt,
                    'durchschnittliche_fahrtdistanz_mit_lk': durchschnittliche_fahrtdistanz_mit_lk,
                    'durchschnittliche_fahrtdistanz_mit_bk': durchschnittliche_fahrtdistanz_mit_bk,
                    'personenkilometer_gefahren': personenkilometer_gefahren,
                    'leerkilometeranteil': leerkilometeranteil,
                    'buendelungsquote': buendelungsquote,
                    'besetzungsquote': besetzungsquote
                })


                #Zeige den Sitzungszustand
                #st.write(st.session_state)

                st.info("""
                    **Hinweis:**
                    Die folgenden Formeln wurden zur Berechnung der Fahrzeugflotten- und Fahrtleistungsdaten verwendet:
                    - **Fahrzeugkilometer gesamt** = Kilometer leer + Kilometer besetzt
                    - **Durchschnittliche Fahrtdistanz je Buchung (einschl. Leerkilometer)** = Fahrzeugkilometer gesamt / Abgeschlossene Buchungen
                    - **Durchschnittliche Fahrtdistanz je Buchung (ohne Leerkilometer)** = Kilometer besetzt / Abgeschlossene Buchungen
                    - **Personenkilometer gefahren** = (Kilometer besetzt / Abgeschlossene Buchungen) * Transportierte Fahrgäste      
                    - **Leerkilometeranteil** = Kilometer leer / Fahrzeugkilometer gesamt
                    - **Bündelungsquote (nach § 50 Absatz 3 PBefG)** = Personenkilometer gefahren / Fahrzeugkilometer gesamt
                    - **Besetzungsquote (nach H Kripoo, 2021)** = Personenkilometer / Kilometer besetzt
                    - **Benzinverbrauch des Ridepooling-Systems** = Σ (Benzinverbrauch * (Kilometer besetzt + Kilometer leer) / 100)
                    - **Dieselverbrauch des Ridepooling-Systems** = Σ (Dieselverbrauch * (Kilometer besetzt + Kilometer leer) / 100)
                    - **Stromverbrauch des Ridepooling-Systems** = Σ (Stromverbrauch * (Kilometer besetzt + Kilometer leer) / 100)
                   
                """)

            except ValueError:
                st.error("Bitte geben Sie gültige Zahlenwerte ein.")
            

def show_emissions_data():
    with st.expander("**1.4 Emissionsdaten**"):
        st.info("**Hinweis:** Bitte geben Sie die CO2eq-Emissionsdaten für Benzin, Diesel und Strom an. Sie können vorausgewählte Optionen wählen oder eigene Angaben tätigen. Optional können Sie auch den Anteil an selbst erzeugtem Strom aus Photovoltaikanlagen angeben, um den adjustierten CO2eq-Emissionsfaktor für Strom zu berechnen. Bitte berücksichtigen Sie die Betrachtungsweise/Analyseprinzip. Dieses Programm nutzt die Well-to-Wheel-Betrachtung (WTW).")

        # CO2eq-Emissionsdaten (Benzin)
        benzin_emissionsdaten_auswahl = st.selectbox("CO2eq-Emissionsdaten (Benzin):", 
                                                      ["Helmholtz-Gemeinschaft Deutscher Forschungszentren [CO2eq]", "CO2eqonline [CO2eq]", "Eigene Angaben"])
        if benzin_emissionsdaten_auswahl == "Helmholtz-Gemeinschaft Deutscher Forschungszentren [CO2eq]":
            benzin_emissionsdaten = 3030  # g/l
        elif benzin_emissionsdaten_auswahl == "CO2online [CO2eq]":
            benzin_emissionsdaten = 2370  # g/l
        else:  # Eigene Angaben
            benzin_emissionsdaten = st.number_input("Geben Sie die CO2-Emissionsdaten (Benzin) [g/l] ein:", min_value=0, step=1)

        # CO2eq-Emissionsdaten (Diesel)
        diesel_emissionsdaten_auswahl = st.selectbox("CO2eq-Emissionsdaten (Diesel):", 
                                                      ["Helmholtz-Gemeinschaft Deutscher Forschungszentren [CO2eq]", "CO2eqonline [CO2eq]", "Eigene Angaben"])
        if diesel_emissionsdaten_auswahl == "Helmholtz-Gemeinschaft Deutscher Forschungszentren [CO2eq]":
            diesel_emissionsdaten = 3410  # g/l
        elif diesel_emissionsdaten_auswahl == "CO2eqonline [CO2eq]":
            diesel_emissionsdaten = 2650  # g/l
        else:  # Eigene Angaben
            diesel_emissionsdaten = st.number_input("Geben Sie die CO2-Emissionsdaten (Diesel) [g/l] ein:", min_value=0, step=1)


        # CO2eq-Emissionsdaten (Strom)
        strom_emissionsdaten_auswahl = st.selectbox("CO2eq-Emissionsdaten (Strom):", 
                                                     ["Umweltbundesamt: CO2eq-Äquivalente mit Vorketten (2022) [CO2eq]", 
                                                      "Umweltbundesamt: CO2eq-Emissionsfaktor Strommix (2022)", 
                                                      "Eigene Angaben"])
        if strom_emissionsdaten_auswahl == "Umweltbundesamt: CO2eq-Äquivalente mit Vorketten (2022) [CO2eq]":
            strom_emissionsdaten = 498  # g/kWh
        elif strom_emissionsdaten_auswahl == "Umweltbundesamt: CO2eq-Emissionsfaktor Strommix (2022)":
            strom_emissionsdaten = 434  # g/kWh
        else:  # Eigene Angaben
            strom_emissionsdaten = st.number_input("Geben Sie die CO2-Emissionsdaten (Strom) [g CO2eq/kWh] ein:", min_value=0, step=1)

        # Anteil an selbst erzeugtem Strom aus Photovoltaikanlagen
        oekostrom_anteil = st.slider("Anteil des selbst erzeugten Stroms aus Photovoltaikanlagen [%]:", min_value=0, max_value=100, value=0, step=1)
        pv_emissionsdaten = st.number_input("Geben Sie die CO2eq-Emissionsdaten für selbst erzeugten Strom aus Photovoltaikanlagen [g/kWh] ein:", value=35.0, min_value=0.0, format='%.1f', step=0.1)

        # Berechnung des adjustierten CO2eq-Emissionsfaktors für Strom
        strom_emissionsdaten = round(strom_emissionsdaten * (1 - oekostrom_anteil / 100.0) + pv_emissionsdaten * (oekostrom_anteil / 100.0), 1)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**CO2eq-Emissionsdaten (Benzin) ausgewählt:**")
        with col2:
            st.write(f"**{benzin_emissionsdaten} g/l**")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**CO2eq-Emissionsdaten (Diesel) ausgewählt:**")
        with col2:
            st.write(f"**{diesel_emissionsdaten} g/l**")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**Adjustierter CO2eq-Emissionsdaten (Strom) basierend auf {oekostrom_anteil}% selbst erzeugtem Strom aus Photovoltaikanlagen:**")
        with col2:
            st.write(f"**{strom_emissionsdaten} g/kWh**")

        st.info("Die Daten für den CO2eq-Wert aus Photovoltaikanlagen stammen von: [Electricity Maps](https://app.electricitymaps.com/zone/DE)")

        # Speichern der globalen Variablen
        st.session_state.update({
            'benzin_emissionsdaten': benzin_emissionsdaten,
            'diesel_emissionsdaten': diesel_emissionsdaten,
            'strom_emissionsdaten': strom_emissionsdaten,
            'oekostrom_anteil': oekostrom_anteil,
            'pv_emissionsdaten': pv_emissionsdaten
        })

def show_environmental_impact_calculation():
    with st.expander("**1.5 Berechnung Umweltwirkung Ridepooling-System**"):
        st.info("**Hinweis:** Im Folgenden ist die Umweltwirkung des Ridepooling-Systems dargestellt. In der Abbildung wird der spezifische CO2-Ausstoß des Ridepooling-Systems denen anderer Verkehrsmittel gegenübergestellt. Die Daten der anderen Verkehrsmittel stammen vom Umweltbundesamt, Umweltfreundlich mobil! (2022).")

        # Stellen Sie sicher, dass alle erforderlichen Werte vorhanden sind, bevor Sie fortfahren
        required_keys = ['fahrzeugkilometer_gesamt', 'personenkilometer_gefahren', 'benzin_emissionsdaten', 'diesel_emissionsdaten', 'strom_emissionsdaten', 'oekostrom_anteil']
        missing_keys = [key for key in required_keys if key not in st.session_state]
        
        if missing_keys:
            st.error(f"Die folgenden Schlüssel fehlen: {', '.join(missing_keys)}")
        else:
            # Abrufen der Werte aus dem Sitzungszustand
            fahrzeugkilometer_gesamt = st.session_state['fahrzeugkilometer_gesamt']
            personenkilometer_gefahren = st.session_state['personenkilometer_gefahren']
            benzinverbrauch_gesamt = float(st.session_state['benzinverbrauch_gesamt'])
            dieselverbrauch_gesamt = float(st.session_state['dieselverbrauch_gesamt'])
            stromverbrauch_gesamt = float(st.session_state['stromverbrauch_gesamt'])
            benzin_emissionsdaten = st.session_state['benzin_emissionsdaten']
            diesel_emissionsdaten = st.session_state['diesel_emissionsdaten']
            strom_emissionsdaten = st.session_state['strom_emissionsdaten']
            oekostrom_anteil = st.session_state['oekostrom_anteil']

            benzin_emissionen = (benzinverbrauch_gesamt * benzin_emissionsdaten) / 1000  # kg CO2e
            diesel_emissionen = (dieselverbrauch_gesamt * diesel_emissionsdaten) / 1000  # kg CO2e
            strom_emissionen = (stromverbrauch_gesamt * strom_emissionsdaten) / 1000  # kg CO2e
            strom_emissionen *= (1 - oekostrom_anteil / 100)  # Anpassung für Ökostrom

            # Speichern als globale Variablen
            st.session_state.update({
                'benzin_emissionen': benzin_emissionen,
                'diesel_emissionen': diesel_emissionen,
                'strom_emissionen': strom_emissionen
            })

            CO2eq_emissionen_gesamt_rps = round(benzin_emissionen + diesel_emissionen + strom_emissionen, 4)
            CO2eq_emissionen_pro_personenkilometer_rps = round(CO2eq_emissionen_gesamt_rps / personenkilometer_gefahren, 4) if personenkilometer_gefahren else 0

            # Umrechnung in g CO2ee pro Pkm
            CO2eq_emissionen_pro_personenkilometer_rps_g = CO2eq_emissionen_pro_personenkilometer_rps * 1000  # Umrechnung in g CO2ee/Pkm

            # Speichern der berechneten Werte im Sitzungszustand
            st.session_state.update({
                'CO2eq_emissionen_gesamt_rps': CO2eq_emissionen_gesamt_rps,
                'CO2eq_emissionen_pro_personenkilometer_rps_g': CO2eq_emissionen_pro_personenkilometer_rps_g
            })

            # Emissionen pro pkm für verschiedene Verkehrsträger
            emissionen_data = {
                st.session_state['name_ridepooling_system']: CO2eq_emissionen_pro_personenkilometer_rps_g,
                'MIV (Fahrer)': 152.86,
                'Bus': 80.54,
                'Straßenbahn/U-Bahn': 59.30,
                'E-Bike/Pedelecs': 3.9,
                'E-Lastenrad': 3.9,
                'Fahrrad': 0.0,
                'Zu Fuß': 0.0
            }

            # Erstellung des ersten Diagramms
            fig1 = go.Figure()
            for verkehrsmittel, emissionen in emissionen_data.items():
                fig1.add_trace(go.Bar(name=verkehrsmittel, x=[verkehrsmittel], y=[emissionen], marker_line_color='rgb(0,0,0)', marker_line_width=1.5, opacity=0.7))
            fig1.update_layout(
                barmode='group',
                title='Gegenüberstellung der Emissionen pro Personenkilometer nach Verkehrsmittel - Well-to-Wheel (WTW)*',
                legend=dict(
                orientation="v",  # vertikale Anordnung
                y=0.6,  # Positionierung der Legende
                x=1.02,  # Legende rechts vom Diagramm
                xanchor='left',
                yanchor='top'
                ),
                width=650,
                height=650,
                yaxis_title='Emissionen [g CO2e/pkm]',
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig1)

            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Gesamte CO2eq-Emissionen des Ridepooling-Systems:**")
            with col2:
                st.write(f"**{CO2eq_emissionen_gesamt_rps:.2f} kg CO2e**")

            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**CO2eq-Emissionen pro Personenkilometer:**")
            with col2:
                st.write(f"**{CO2eq_emissionen_pro_personenkilometer_rps_g:.2f} g CO2e/pkm**")

# Initialisiere Session State Variablen
initialize_session_state()

# Zeige Sidebar an
show_sidebar()

# Grundlegende Konfiguration
st.title('Entwurf: Vergleich der CO2eq-Emissionen von Bus- und Ridepooling-System')

show_methodik()

st.subheader("1. Berechnung der CO2eq-Emissionen des Ridepooling-Systems")
# Zeige Allgemeine Informationen an
show_general_info()

# Zeige Systemleistungs-Sektion an
show_system_performance()

# Zeige Fahrzeugflotten- und Fahrtleistungs-Sektion an
show_vehicle_fleet_performance()

# Zeige Emissionsdaten-Sektion an
show_emissions_data()

# Zeige Berechnung Umweltwirkung Ridepooling-System an
show_environmental_impact_calculation()



################################################################ Berechnung Bus ################################################################
# Constants
initial_CO2eq_wtw = 80.54  # g CO2eeg/Pkm (Well-to-Wheel)
initial_occupancy = 18.7  # % (VDV Statistik 2022)

# Function to calculate Platzausnutzung
def calculate_platzausnutzung(personen_km, platz_km):
    return (personen_km / platz_km) * 100

# Function to calculate new CO2e emissions based on adjusted Platzausnutzung
def calculate_new_CO2eq_wtw(initial_CO2eq, initial_occupancy, adjusted_occupancy):
    return initial_CO2eq * (initial_occupancy / adjusted_occupancy)

# Part 1: Calculate Platzausnutzung
st.subheader('2. Berechnung CO2eq-Emissionen Bus')
with st.expander('**2.1 Berechnung der durchschnittlichen Platzausnutzung des Bus-Systems**'):
    st.info("**Hinweis:** Die vorausgefüllten Daten beziehen sich auf die durchschnittliche Platzausnutzung im deutschen Durchschnitt (VDV Statistik 2022). Sie können die durchschnittliche Platzausnutzung spezifisch für Ihr Bussystem berechnen. Sie können den errechneten Wert im folgenden Schritt einsetzen, um einen Vergleich der CO2eq-Emissionen zu erhalten.")
    # Eingabefelder für Personen- und Platzkilometer
    
    Nutzwagen_km = st.number_input("Nutzwagenkilometer [Mio.]", min_value=0.0, value=1658.0, step=0.1, format="%.1f")
    st.caption("Anzahl der Kilometer im Linienverkehr zurückgelegten Produktivkilometer. Dazu kommen dann noch die Leerkilometer (Einsatzfahrten etc.), die die Verkehrsleistung des Unternehmens beschreiben (Glossar des Nahverkehrs, RVM 2024)")
    
    Platzangebot= st.number_input("Platzangebot (Sitz- und Stehplätze) der einzelnen Fahrzeuge", min_value=0.0, value=78.5186, step=0.1, format="%.2f")
    st.caption("Anzahl der durchschnittlichen Sitz- und Stehplätze der einzelnen Fahrzeuge.")

    personen_km = st.number_input("Personenkilometer [Mio.]", min_value=0.0, value=24311.0, step=0.1, format="%.1f")
    st.caption("Produkt aus beförderten Personen und der zurückgelegten Entfernung in Kilometern.")
    
    # Berechnung der Platzkilometer
    platz_km = Nutzwagen_km * Platzangebot
    col1, col2 = st.columns([3, 1])
    # Anzeige der berechneten Platzkilometer
    with col1:
        st.write("**Berechnete Platzkilometer [Mio.]:**")
    with col2:
        st.write(f"{platz_km:.2f}")

    st.caption("Produkt aus Nutzwagenkilometer und Platzangebot (Sitz- und Stehplätze) jeweils der einzelnen Fahrzeuge (Berechnung nach VDV-Richtlinien von 1990).")

    # Berechnung der Platzausnutzung
    calculated_occupancy = calculate_platzausnutzung(personen_km, platz_km)
    col1, col2 = st.columns([3, 1])
    # Anzeige der berechneten durchschnittlichen Platzausnutzung
    with col1:
        st.write("**Berechnete durchschnittliche Platzausnutzung:**")
    with col2:
        st.write(f"{calculated_occupancy:.2f}%")
    st.caption("Berechnet als (Personenkilometer / Platzkilometer) * 100.")

    # Erklärung der Berechnungen
    st.info("""
    **Berechnungen:**
    - **Personenkilometer**: Das Produkt aus beförderten Personen und der zurückgelegten Entfernung in Kilometern.
    - **Platzkilometer**: Das Produkt aus Nutzwagenkilometern und der Platzangebot (Sitz- und Stehplätze) der einzelnen Fahrzeuge.
    - **Durchschnittliche Platzausnutzung**: Wird berechnet als (Personenkilometer / Platzkilometer) * 100.
    - **CO2eq-Ausstoß (WTW)**: Basierend auf der durchschnittlichen Platzausnutzung in Deutschland (18.7 %, VDV Statistik 2022), wird der CO2eq-Wert (80.54 g CO2eq/Pkm, Umweltfreundlich mobil! Umweltbundesamt, 2021) auf Basis der WTW-Betrachtung angepasst.
    """)

    # Part 2: Adjust Platzausnutzung and calculate CO2e emissions
with st.expander('**2.2 Anpassung der Platzausnutzung und CO2eq-Emissionen**'):
    st.info("**Hinweis:** Passen Sie die durchschnittliche Platzausnutzung Ihres Bussystems an, um den neuen CO2eq-Wert zu berechnen. Dieser angepasste CO2eq-Wert wird anschließend mit dem CO2eq-Ausstoß des Ridepooling-Systems verglichen. Voreingestellt sind die bundesweiten Werte, welche bei der Berechnung des Umweltbundesamtes ('umweltfreundlich mobil!', 2022) hinterlegt sind.")
    adjusted_occupancy = st.slider("Angepasste durchschnittliche Platzausnutzung (%)", min_value=0.1, max_value=100.0, value=initial_occupancy, step=0.1)
    st.caption("Passen Sie die durchschnittliche Platzausnutzung an, um den neuen CO2eq-Wert zu berechnen.")

    # Berechnung des neuen CO2eq-Wertes basierend auf der angepassten Platzausnutzung
    new_CO2eq_wtw = calculate_new_CO2eq_wtw(initial_CO2eq_wtw, initial_occupancy, adjusted_occupancy)

    # Erstelle zwei Spalten für die Anzeige
    col1, col2 = st.columns([3, 1])

    # Anzeige des angepassten CO2eq-Ausstoßes
    with col1:
        st.write(f"**Angepasster CO2eq-Ausstoß (WTW) bei {adjusted_occupancy:.2f}% Platzausnutzung:**")
    with col2:
        st.write(f"{new_CO2eq_wtw:.2f} g CO2eq/Pkm")


    ################################################################ Vergleich ################################################################
st.subheader('3. Vergleich der CO2eq-Emissionen')

with st.expander("**3.1 Vergleich der CO2eq-Emissionen von Bus und Ridepooling-System**"):

    def compare_emissions():
        if 'CO2eq_emissionen_pro_personenkilometer_rps_g' not in st.session_state:
            st.error("CO2eq-Emissionen des Ridepooling-Systems sind nicht verfügbar.")
            return
        st.info("**Hinweis:** Im Folgenden wird der CO2eq-Ausstoß des Bus-Systems mit dem CO2eq-Ausstoß des Ridepooling-Systems verglichen. Die Daten für das Bus-System werden in Kapitel 2 berechnet, die des Ridepooling-Systems in Abschnitt 1.")
        #Nimm den Namen des Ridepooling-Systems aus dem Sitzungszustand
        name_ridepooling_system = st.session_state['name_ridepooling_system']

        # Erstellung des Diagramms
        fig2 = go.Figure()
        ridepooling_system_name = "Ridepooling-System"
        fig2.add_trace(go.Bar(name=name_ridepooling_system, x=[name_ridepooling_system], y=[st.session_state['CO2eq_emissionen_pro_personenkilometer_rps_g']], marker_line_color='rgb(0,0,0)', marker_line_width=1.5, opacity=0.7))
        fig2.add_trace(go.Bar(name='Bus', x=['Bus'], y=[new_CO2eq_wtw], marker_line_color='rgb(0,0,0)', marker_line_width=1.5, opacity=0.7))
        fig2.update_layout(
            barmode='group',
            title='Vergleich der CO2eq-Emissionen pro Personenkilometer',
            legend=dict(
                orientation="v",  # vertikale Anordnung
                y=0.6,  # Positionierung der Legende
                x=1.02,  # Legende rechts vom Diagramm
                xanchor='left',
                yanchor='top'
            ),
            width=650,
            height=650,
            yaxis_title='Emissionen [g CO2eq/pkm]',
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig2)
            # Erstelle zwei Spalten für jede Zeile
        col1, col2 = st.columns([3, 1])  # Verhältnis 3:1 sorgt dafür, dass die linke Spalte breiter ist
        
        # Erste Zeile
        with col1:
            st.write("**CO2eq-Emissionen Bus (angepasst):**")
        with col2:
            st.write(f"{new_CO2eq_wtw:.2f} g CO2eq/Pkm")
        
        # Zweite Zeile
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("**Platzausnutzung Bus (angepasst):**")
        with col2:
            st.write(f"{adjusted_occupancy:.2f}%")
        
        # Dritte Zeile
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("**Prozentuale Differenz zur durchschnittlichen deutschen Platzausnutzung (18.7 %, VDV Statistik 2022):**")
        with col2:
            st.write(f"{(adjusted_occupancy - initial_occupancy) / initial_occupancy * 100:.2f}%")
        
        # Vierte Zeile
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("**CO2eq-Emissionen Ridepooling-System:**")
        with col2:
            st.write(f"{st.session_state['CO2eq_emissionen_pro_personenkilometer_rps_g']:.2f} g CO2eq/Pkm")

        st.info("""
        **Anmerkungen:**
        - Die Berechnung der CO2eq-Emissionen des Ridepooling-Systems berücksichtigt ausschließlich monomodale Fahrten. Zu- oder Abfahrtswege vor oder nach einer Ridepooling-Fahrt können nicht berücksichtigt werden.
        - Die Umweltwirkung wird anhand der CO2eq-Emissionen bewertet. Andere Umweltkategorien (z.B. Luftschadstoffe, Lärm) werden zur Zeit nicht berücksichtigt.
        - Eine Berücksichtigung von E-Busfahrzeugen geschieht zwar indirekt über die Emissionsdaten des Umweltbundesamt ('umweltfreundlich mobil!', 2022). Die Datengrundlage kann zur Zeit nicht angepasst werden.
        - Die durchschnittliche Platzausnutzung kann lediglich für den 24-Stunden-Betrieb angegeben werden (Umweltbundesamt, 'umweltfreundlich mobil!', 2022). Die Datengrundlage kann zur Zeit nicht angepasst werden.
        """)
    compare_emissions()

# Footer
st.markdown("---")
st.write("***Entwurfsfassung***")
st.write("Dieses Programm wurde  im Projekt 'Bewertung der ökologischen Effekte von Ridepooling-Systemen anhand von vier Fallbeispielen in NRW' entwickelt und durch das Ministerium für Umwelt, Naturschutz, und Verkehr des Landes Nordrhein-Westfalens gefördert. © 2024 [FH Münster](https://www.fh-muenster.de/)")
st.write("Die Berechnungen basieren auf den Annahmen und Daten, die Sie in den verschiedenen Abschnitten des Programms eingegeben haben.")
st.write("Die Ergebnisse dienen nur zu Informationszwecken und sind nicht verbindlich.")
st.write("Für Fragen oder Anregungen wenden Sie sich bitte an [peter.bruder@fh-muenster.de](mailto:peter.bruder@fh-muenster.de).")
