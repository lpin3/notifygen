# Notifygen Mobile

Projeto Flutter inicial para consumir a API mobile deste repositório.

## Ajustes antes de rodar

1. Instale o Flutter no ambiente.
2. Entre em `mobile_app/`.
3. Se quiser gerar as pastas nativas ausentes, execute `flutter create .`.
4. Ajuste `lib/core/config/app_config.dart` com a URL correta da API.
5. Rode `flutter pub get`.
6. Inicie com `flutter run`.

## Fluxo implementado

- Geração e armazenamento de um identificador local do dispositivo.
- Registro do dispositivo na API mobile.
- Ativação do dispositivo com código, matrícula e senha.
- Persistência local de `api_key` e `matricula`.
- Consulta de status, listagem de CRRs e listagem de enquadramentos.

## Observação

O backend atual usa o campo `imei`. Neste app ele é preenchido com um identificador UUID persistido localmente, o que funciona melhor em Flutter do que depender do IMEI real do aparelho.
