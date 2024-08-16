import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Funktionsdefinitionen zur Berechnung der CO2-Emissionen
def calculate_emissions(fuel_consumption_gasoline, emission_factor_gasoline, fuel_consumption_diesel, emission_factor_diesel, fuel_consumption_electric, emission_factor_electric, total_km, occupancy_rate, empty_km):
    occupied_km = total_km - empty_km
    total_fuel_consumed_gasoline = (fuel_consumption_gasoline / 100) * total_km
    total_fuel_consumed_diesel = (fuel_consumption_diesel / 100) * total_km
    total_fuel_consumed_electric = (fuel_consumption_electric / 100) * total_km

    total_emissions_gasoline = total_fuel_consumed_gasoline * emission_factor_gasoline
    total_emissions_diesel = total_fuel_consumed_diesel * emission_factor_diesel
    total_emissions_electric = total_fuel_consumed_electric * emission_factor_electric

    total_emissions = total_emissions_gasoline + total_emissions_diesel + total_emissions_electric
    person_km = occupancy_rate * occupied_km

    emissions_per_pkm = total_emissions / person_km if person_km != 0 else 0
    return emissions_per_pkm, total_emissions, person_km, occupied_km

# Streamlit Inputs
st.title("CO2-Emissionen pro Personenkilometer für Linienbus und Ridepooling-System")
st.header("Eingabewerte")

# Hinweise
st.write("Passen Sie die Verbrauchsdaten an, um zwischen verschiedenen Busmodellen oder Ridepooling-Systemen zu unterscheiden.")

# Tabellenstruktur mit Expandern für Linienbus und Ridepooling-System
col1, col2 = st.columns(2)

with col1:
    with st.expander("Linienbus"):
        st.subheader("Benzin")
        bus_fuel_consumption_gasoline = st.number_input("Treibstoffverbrauch (Liter/100 km)", value=0, key='bus_fuel_consumption_gasoline')
        bus_emission_factor_gasoline = st.number_input("Emissionsfaktor (kg CO2/Liter)", value=3.03, key='bus_emission_factor_gasoline')

        st.subheader("Diesel")
        bus_fuel_consumption_diesel = st.number_input("Treibstoffverbrauch (Liter/100 km)", value=30, key='bus_fuel_consumption_diesel')
        bus_emission_factor_diesel = st.number_input("Emissionsfaktor (kg CO2/Liter)", value=3.41, key='bus_emission_factor_diesel')

        st.subheader("Strom")
        bus_fuel_consumption_electric = st.number_input("Verbrauch (kWh/100 km)", value=0.0, key='bus_fuel_consumption_electric')
        bus_emission_factor_electric = st.number_input("Emissionsfaktor (kg CO2/kWh)", value=0.498, key='bus_emission_factor_electric')

        st.subheader("Allgemeine Eingaben für Linienbus")
        bus_occupied_km = st.number_input("Kilometer (besetzt)", value=90.0, key='bus_occupied_km')
        bus_empty_km = st.number_input("Kilometer (leer)", value=10.0, key='bus_empty_km')
        bus_total_km = bus_occupied_km + bus_empty_km

        bus_transported_passengers = st.slider("Wähle die Anzahl der transportierten Fahrgäste für Linienbus", min_value=1, max_value=100, value=20, key='bus_transported_passengers')

        # Berechnung der CO2-Emissionen und anderen Kennzahlen für Linienbus
        selected_emission_bus, total_emissions_bus, person_km_bus, occupied_km_bus = calculate_emissions(
            bus_fuel_consumption_gasoline, bus_emission_factor_gasoline,
            bus_fuel_consumption_diesel, bus_emission_factor_diesel,
            bus_fuel_consumption_electric, bus_emission_factor_electric,
            bus_total_km, bus_transported_passengers, bus_empty_km
        )

        leerkilometeranteil_bus = round((bus_empty_km / bus_total_km) * 100, 2) if bus_total_km > 0 else 0
        buendelungsquote_bus = round(person_km_bus / bus_total_km, 2) if bus_total_km > 0 else 0
        besetzungsquote_bus = round(person_km_bus / occupied_km_bus, 2) if occupied_km_bus > 0 else 0

        st.write(f"CO2-Emissionen bei {bus_transported_passengers} transportierten Fahrgästen für Linienbus: {selected_emission_bus:.3f} kg CO2/pkm")
        st.write(f"Personenkilometer für Linienbus: {person_km_bus:.2f} pkm")
        st.write(f"Leerkilometeranteil für Linienbus: {leerkilometeranteil_bus:.2f} %")
        st.write(f"Bündelungsquote für Linienbus: {buendelungsquote_bus:.2f} Personen/km")
        st.write(f"Besetzungsquote für Linienbus: {besetzungsquote_bus:.2f} Personen/km")

with col2:
    with st.expander("Ridepooling-System"):
        st.subheader("Benzin")
        ridepool_fuel_consumption_gasoline = st.number_input("Treibstoffverbrauch (Liter/100 km)", value=1.2, key='ridepool_fuel_consumption_gasoline')
        ridepool_emission_factor_gasoline = st.number_input("Emissionsfaktor (kg CO2/Liter)", value=3.03, key='ridepool_emission_factor_gasoline')

        st.subheader("Diesel")
        ridepool_fuel_consumption_diesel = st.number_input("Treibstoffverbrauch (Liter/100 km)", value=0, key='ridepool_fuel_consumption_diesel')
        ridepool_emission_factor_diesel = st.number_input("Emissionsfaktor (kg CO2/Liter)", value=3.41, key='ridepool_emission_factor_diesel')

        st.subheader("Strom")
        ridepool_fuel_consumption_electric = st.number_input("Verbrauch (kWh/100 km)", value=20.5, key='ridepool_fuel_consumption_electric')
        ridepool_emission_factor_electric = st.number_input("Emissionsfaktor (kg CO2/kWh)", value=0.498, key='ridepool_emission_factor_electric')

        st.subheader("Allgemeine Eingaben für Ridepooling-System")
        ridepool_occupied_km = st.number_input("Kilometer (besetzt)", value=70.0, key='ridepool_occupied_km')
        ridepool_empty_km = st.number_input("Kilometer (leer)", value=30.0, key='ridepool_empty_km')
        ridepool_total_km = ridepool_occupied_km + ridepool_empty_km

        ridepool_transported_passengers = st.slider("Wähle die Anzahl der transportierten Fahrgäste für Ridepooling-System", min_value=1, max_value=100, value=20, key='ridepool_transported_passengers')

        # Berechnung der CO2-Emissionen und anderen Kennzahlen für Ridepooling-System
        selected_emission_ridepool, total_emissions_ridepool, person_km_ridepool, occupied_km_ridepool = calculate_emissions(
            ridepool_fuel_consumption_gasoline, ridepool_emission_factor_gasoline,
            ridepool_fuel_consumption_diesel, ridepool_emission_factor_diesel,
            ridepool_fuel_consumption_electric, ridepool_emission_factor_electric,
            ridepool_total_km, ridepool_transported_passengers, ridepool_empty_km
        )

        leerkilometeranteil_ridepool = round((ridepool_empty_km / ridepool_total_km) * 100, 2) if ridepool_total_km > 0 else 0
        buendelungsquote_ridepool = round(person_km_ridepool / ridepool_total_km, 2) if ridepool_total_km > 0 else 0
        besetzungsquote_ridepool = round(person_km_ridepool / occupied_km_ridepool, 2) if occupied_km_ridepool > 0 else 0

        st.write(f"CO2-Emissionen bei {ridepool_transported_passengers} transportierten Fahrgästen für Ridepooling-System: {selected_emission_ridepool:.3f} kg CO2/pkm")
        st.write(f"Personenkilometer für Ridepooling-System: {person_km_ridepool:.2f} pkm")
        st.write(f"Leerkilometeranteil für Ridepooling-System: {leerkilometeranteil_ridepool:.2f} %")
        st.write(f"Bündelungsquote für Ridepooling-System: {buendelungsquote_ridepool:.2f} Personen/km")
        st.write(f"Besetzungsquote für Ridepooling-System: {besetzungsquote_ridepool:.2f} Personen/km")

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(np.linspace(1, 100, 100), [calculate_emissions(
    bus_fuel_consumption_gasoline, bus_emission_factor_gasoline,
    bus_fuel_consumption_diesel, bus_emission_factor_diesel,
    bus_fuel_consumption_electric, bus_emission_factor_electric,
    bus_total_km, o, bus_empty_km)[0] for o in np.linspace(1, 100, 100)], label='Linienbus')
plt.plot(np.linspace(1, 100, 100), [calculate_emissions(
    ridepool_fuel_consumption_gasoline, ridepool_emission_factor_gasoline,
    ridepool_fuel_consumption_diesel, ridepool_emission_factor_diesel,
    ridepool_fuel_consumption_electric, ridepool_emission_factor_electric,
    ridepool_total_km, o, ridepool_empty_km)[0] for o in np.linspace(1, 100, 100)], label='Ridepooling-System')
plt.xlabel('Transportierte Fahrgäste')
plt.ylabel('CO2-Emissionen pro Personenkilometer (kg CO2/pkm)')
plt.title('CO2-Emissionen pro Personenkilometer bei verschiedenen Transportierte Fahrgäste')
plt.legend()
plt.grid(True)

plt.axvline(x=bus_transported_passengers, color='b', linestyle='--')
plt.scatter([bus_transported_passengers], [selected_emission_bus], color='blue')  # Punkt markieren
plt.annotate(f'{selected_emission_bus:.3f} kg CO2/pkm (Bus)', 
             xy=(bus_transported_passengers, selected_emission_bus), 
             xytext=(bus_transported_passengers + 5, selected_emission_bus + 0.05),
             arrowprops=dict(facecolor='black', shrink=0.05))

plt.axvline(x=ridepool_transported_passengers, color='r', linestyle='--')
plt.scatter([ridepool_transported_passengers], [selected_emission_ridepool], color='orange')  # Punkt markieren
plt.annotate(f'{selected_emission_ridepool:.3f} kg CO2/pkm (Ridepooling)', 
             xy=(ridepool_transported_passengers, selected_emission_ridepool), 
             xytext=(ridepool_transported_passengers + 5, selected_emission_ridepool + 0.05),
             arrowprops=dict(facecolor='black', shrink=0.05))

st.pyplot(plt)
