# AWS Polly Voice Options for Miro

## Popular Multilingual Neural Voices

### English
- **Joanna** (en-US) - Female, friendly
- **Matthew** (en-US) - Male, clear
- **Amy** (en-GB) - Female, British
- **Brian** (en-GB) - Male, British
- **Olivia** (en-AU) - Female, Australian

### Spanish
- **Lucia** (es-ES) - Female, European Spanish
- **Sergio** (es-ES) - Male, European Spanish
- **Mia** (es-MX) - Female, Mexican Spanish
- **Andres** (es-MX) - Male, Mexican Spanish
- **Lupe** (es-US) - Female, US Spanish

### French
- **Lea** (fr-FR) - Female
- **Remi** (fr-FR) - Male
- **Gabrielle** (fr-CA) - Female, Canadian

### German
- **Vicki** (de-DE) - Female
- **Daniel** (de-DE) - Male

### Italian
- **Bianca** (it-IT) - Female
- **Adriano** (it-IT) - Male

### Portuguese
- **Camila** (pt-BR) - Female, Brazilian
- **Vitoria** (pt-BR) - Female, Brazilian
- **Thiago** (pt-BR) - Male, Brazilian
- **Ines** (pt-PT) - Female, European Portuguese

### Hindi
- **Kajal** (hi-IN) - Female
- **Aditi** (hi-IN) - Female (also supports bilingual)

### Arabic
- **Zeina** (arb) - Female, Modern Standard Arabic

### Chinese
- **Zhiyu** (cmn-CN) - Female, Mandarin

### Japanese
- **Takumi** (ja-JP) - Male
- **Kazuha** (ja-JP) - Female

### Korean
- **Seoyeon** (ko-KR) - Female

### Dutch
- **Laura** (nl-NL) - Female

### Polish
- **Ola** (pl-PL) - Female

### Russian
- **Tatyana** (ru-RU) - Female

### Turkish
- **Filiz** (tr-TR) - Female

### Swedish
- **Elin** (sv-SE) - Female

### Norwegian
- **Ida** (nb-NO) - Female

### Danish
- **Naja** (da-DK) - Female

## How to Use

Update your `.env` file with the desired voice:

```env
ENABLE_TTS=true
TTS_VOICE_ID=Joanna
TTS_ENGINE=neural
TTS_LANGUAGE_CODE=en-US
```

For example, to use Hindi:
```env
TTS_VOICE_ID=Kajal
TTS_LANGUAGE_CODE=hi-IN
```

For Spanish (Mexico):
```env
TTS_VOICE_ID=Mia
TTS_LANGUAGE_CODE=es-MX
```

## Notes

- **Neural engine** provides the most natural-sounding voices
- Some voices support multiple languages (bilingual)
- Language code must match the voice's supported language
- Neural voices may have slightly higher costs than standard voices
- All neural voices support SSML for advanced pronunciation control

## Cost Considerations

AWS Polly Neural voices pricing (as of 2024):
- $16.00 per 1 million characters
- First 1 million characters per month are free (12-month free tier)

For a typical 100-character response:
- 10,000 responses = $0.16
- Very affordable for educational use!
