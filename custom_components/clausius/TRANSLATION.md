# Translations / Tłumaczenia

## 🌍 Supported Languages / Obsługiwane języki

- **English (en)** - Default / Domyślny
- **Polish (pl)** - Polski

## 📁 File Structure / Struktura plików

```
custom_components/clausius/
├── strings.json              # English (default) / Angielski (domyślny)
└── translations/
    ├── en.json               # English / Angielski (optional, falls back to strings.json)
    ├── pl.json               # Polish / Polski
    └── template.json         # Template for new languages / Szablon dla nowych języków
```

## 🔧 How It Works / Jak to działa

Home Assistant automatycznie wybiera język na podstawie ustawień użytkownika:
1. Home Assistant sprawdza ustawienia języka użytkownika (Settings → System → General → Language)
2. Jeśli istnieje plik `translations/{language_code}.json`, używa go
3. W przeciwnym razie używa domyślnego pliku `strings.json` (angielski)

## ➕ Adding a New Language / Dodawanie nowego języka

### Method 1: Using Template / Metoda 1: Użycie szablonu

1. Copy `translations/template.json` to `translations/{language_code}.json`
   Skopiuj `translations/template.json` do `translations/{kod_języka}.json`
   
   Example / Przykład:
   ```bash
   cp translations/template.json translations/de.json  # German/Niemiecki
   cp translations/template.json translations/fr.json  # French/Francuski
   cp translations/template.json translations/es.json  # Spanish/Hiszpański
   ```

2. Replace all `[TRANSLATE]` markers with translated text
   Zamień wszystkie znaczniki `[TRANSLATE]` na przetłumaczony tekst

3. Test the integration with the new language
   Przetestuj integrację z nowym językiem

### Method 2: Copy from English / Metoda 2: Kopiowanie z angielskiego

1. Copy `strings.json` to `translations/{language_code}.json`
   Skopiuj `strings.json` do `translations/{kod_języka}.json`

2. Translate all text values while keeping the JSON structure
   Przetłumacz wszystkie wartości tekstowe zachowując strukturę JSON

## 📝 Language Codes / Kody języków

Common language codes / Popularne kody języków:
- `en` - English / Angielski
- `pl` - Polish / Polski
- `de` - German / Niemiecki
- `fr` - French / Francuski
- `es` - Spanish / Hiszpański
- `it` - Italian / Włoski
- `nl` - Dutch / Holenderski
- `cs` - Czech / Czeski
- `sk` - Slovak / Słowacki
- `ru` - Russian / Rosyjski
- `uk` - Ukrainian / Ukraiński

Full list: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes

## 🧪 Testing Translations / Testowanie tłumaczeń

1. Change Home Assistant language:
   Zmień język Home Assistant:
   - Go to / Przejdź do: Settings → System → General → Language
   - Select your language / Wybierz swój język
   - Reload integration / Przeładuj integrację

2. Verify all strings are translated:
   Sprawdź czy wszystkie teksty są przetłumaczone:
   - Configuration flow (when adding integration)
     Przepływ konfiguracji (podczas dodawania integracji)
   - Entity names in UI
     Nazwy encji w interfejsie
   - Options flow (integration settings)
     Przepływ opcji (ustawienia integracji)

## 🎯 Translation Keys / Klucze tłumaczeń

### Configuration Flow / Przepływ konfiguracji
- `config.step.user.title` - Dialog title / Tytuł okna dialogowego
- `config.step.user.description` - Dialog description / Opis okna
- `config.step.user.data.*` - Input field labels / Etykiety pól wejściowych
- `config.error.*` - Error messages / Komunikaty błędów

### Options Flow / Przepływ opcji
- `options.step.init.title` - Options dialog title / Tytuł okna opcji
- `options.step.init.data.*` - Option field labels / Etykiety pól opcji

### Entity Names / Nazwy encji
- `entity.sensor.clausius_*` - Sensor entity names / Nazwy encji sensorów

## 🤝 Contributing Translations / Współpraca przy tłumaczeniach

To contribute a new translation / Aby dodać nowe tłumaczenie:

1. Fork the repository / Zforkuj repozytorium
2. Create a new translation file / Stwórz nowy plik tłumaczenia
3. Translate all strings / Przetłumacz wszystkie teksty
4. Test the translation / Przetestuj tłumaczenie
5. Submit a Pull Request / Wyślij Pull Request

## ⚠️ Important Notes / Ważne uwagi

- **Keep JSON structure intact** / Zachowaj strukturę JSON
  Do not modify keys, only translate values
  Nie modyfikuj kluczy, tłumacz tylko wartości

- **Use proper encoding** / Użyj właściwego kodowania
  All files must be UTF-8 encoded
  Wszystkie pliki muszą być zakodowane w UTF-8

- **Test before submitting** / Przetestuj przed wysłaniem
  Always test translations in Home Assistant
  Zawsze testuj tłumaczenia w Home Assistant

- **Special characters** / Znaki specjalne
  JSON requires escaping special characters: `"` → `\"`
  JSON wymaga escapowania znaków specjalnych: `"` → `\"`

## 📚 Examples / Przykłady

### English (en)
```json
{
  "config": {
    "step": {
      "user": {
        "title": "Clausius Heat Pump Configuration"
      }
    }
  }
}
```

### Polish (pl)
```json
{
  "config": {
    "step": {
      "user": {
        "title": "Konfiguracja pompy ciepła Clausius"
      }
    }
  }
}
```

### German (de)
```json
{
  "config": {
    "step": {
      "user": {
        "title": "Clausius Wärmepumpe Konfiguration"
      }
    }
  }
}
```

## 🔗 Resources / Zasoby

- [Home Assistant Translation Guidelines](https://developers.home-assistant.io/docs/internationalization/)
- [ISO 639-1 Language Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
- [JSON Validator](https://jsonlint.com/)

## 💬 Questions? / Pytania?

If you have questions about translations, please:
Jeśli masz pytania dotyczące tłumaczeń:
- Open an issue on GitHub / Otwórz issue na GitHub
- Join our discussions / Dołącz do dyskusji