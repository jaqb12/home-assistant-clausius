# Integracja Home Assistant dla pompy ciepła Clausius

Ta integracja umożliwia odczyt danych z pompy ciepła Clausius w Home Assistant poprzez interfejs webowy.

## Wymagania

- Home Assistant Core 2023.1 lub nowszy
- Dostęp do interfejsu webowego pompy ciepła Clausius
- Dane logowania do portalu Clausius

## Instalacja

### Opcja 1: HACS (Zalecane)

1. Zainstaluj HACS w Home Assistant
2. Przejdź do HACS > Integrations
3. Kliknij "+" i wyszukaj "Clausius Heat Pump"
4. Zainstaluj integrację
5. Zrestartuj Home Assistant

### Opcja 2: Ręczna instalacja

1. Pobierz kod źródłowy integracji
2. Skopiuj folder `custom_components/clausius/` do katalogu `config/custom_components/` w Home Assistant
3. Zrestartuj Home Assistant

## Konfiguracja

### Przez interfejs Home Assistant

1. Przejdź do Ustawienia > Urządzenia i usługi
2. Kliknij "Dodaj integrację"
3. Wyszukaj "Clausius Heat Pump" lub "Clausius"
4. Postępuj zgodnie z instrukcjami konfiguracji

### Parametry konfiguracji

| Parametr | Opis | Wymagany | Domyślny |
|----------|------|----------|----------|
| Host | Adres IP lub hostname pompy ciepła | Tak | - |
| Port | Port HTTP interfejsu | Tak | 8080 |
| Nazwa użytkownika | Nazwa użytkownika do logowania | Tak | - |
| Hasło | Hasło użytkownika | Tak | - |
| Interwał odświeżania | Częstotliwość odczytu danych (sekundy) | Nie | 60 |

## Encje

Integracja tworzy następujące encje:

### Sensory temperatury
- `sensor.clausius_outside_temp` - Temperatura zewnętrzna (°C)
- `sensor.clausius_cwu_temp` - Temperatura CWU (°C)

### Sensory statusu
- `sensor.clausius_on_off` - Stan zasilania (On/Off)
- `sensor.clausius_mode` - Tryb pracy (Zima/Lato/Automatyczny)
- `sensor.clausius_compressor_status` - Status kompresora
- `sensor.clausius_pump_status` - Status pompy

### Sensory pomiarów
- `sensor.clausius_pump_level` - Poziom pompy
- `sensor.clausius_glycol_pressure` - Ciśnienie glikolu (bar)

### Sensory SPF
- `sensor.clausius_spf_day` - Dzienny SPF
- `sensor.clausius_spf_month` - Miesięczny SPF
- `sensor.clausius_spf_year` - Roczny SPF

## Przykłady użycia

### Karta w Lovelace UI

```yaml
type: entities
entities:
  - entity: sensor.clausius_outside_temp
    name: Temperatura zewnętrzna
  - entity: sensor.clausius_cwu_temp
    name: Temperatura CWU
  - entity: sensor.clausius_on_off
    name: Zasilanie
  - entity: sensor.clausius_mode
    name: Tryb pracy
  - entity: sensor.clausius_compressor_status
    name: Kompresor
header: Pompa ciepła Clausius
```

### Automatyzacja

```yaml
alias: Powiadomienie o wysokiej temperaturze CWU
description: Powiadom, gdy temperatura CWU przekroczy 60°C
trigger:
  - platform: numeric_state
    entity_id: sensor.clausius_cwu_temp
    above: 60
action:
  - service: notify.persistent_notification
    data:
      message: "Temperatura CWU: {{ states('sensor.clausius_cwu_temp') }}°C"
      title: ⚠️ Wysoka temperatura CWU
```

## Rozwiązywanie problemów

### Błędy połączenia
- Sprawdź adres IP i port pompy ciepła
- Upewnij się, że interfejs webowy pompy jest dostępny
- Sprawdź dane logowania

### Brak danych
- Sprawdź logi Home Assistant (Ustawienia > Dzienniki)
- Upewnij się, że interwał odświeżania nie jest zbyt krótki
- Sprawdź czy struktura strony się nie zmieniła

### Zgłaszanie błędów
Jeśli napotkasz problemy:
1. Sprawdź logi Home Assistant
2. Otwórz issue na GitHub
3. Dołącz logi błędów i informacje o konfiguracji

## Migracja z variables addona

Jeśli wcześniej używałeś variables addona:

1. Usuń konfigurację variables z `configuration.yaml`
2. Usuń plik `var_clausius.yaml`
3. Zainstaluj tę integrację
4. Skonfiguruj przez interfejs HA
5. Aktualizuj encje w automatyzacjach (zamień `var.clausius_*` na `sensor.clausius_*`)

## Wsparcie

- Dokumentacja: [GitHub Wiki](https://github.com/your_username/home-assistant-clausius/wiki)
- Zgłaszanie błędów: [GitHub Issues](https://github.com/your_username/home-assistant-clausius/issues)
- Wsparcie społeczności: [Forum Home Assistant](https://community.home-assistant.io/)

## Licencja

MIT License - zobacz plik LICENSE dla szczegółów.
