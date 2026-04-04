class AppConfig {
  const AppConfig._();

  // Ajuste para o host do backend Django antes de rodar no dispositivo.
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1/mobile/';
}
