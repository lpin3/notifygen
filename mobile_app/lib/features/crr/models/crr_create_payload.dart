class CrrCreatePayload {
  CrrCreatePayload({
    required this.localFiscalizacao,
    required this.municipioEstadoFiscalizacao,
    required this.dataFiscalizacao,
    required this.horaFiscalizacao,
    required this.matriculaAgente,
    this.numeroCrr = '',
    this.medidaAdministrativa = 'Remocao do veiculo ao Deposito',
    this.localPatio = '',
    this.placaGuincho = '',
    this.encarregado = '',
    this.observacao = '',
    this.placa = '',
    this.chassi = '',
    this.marca = '',
    this.modelo = '',
    this.cor = '',
    this.nomeCondutor = '',
    this.cpfCondutor = '',
    this.cnh = '',
    this.cnhEstrangeira = '',
    this.aits = const <String>[],
    this.enquadramentos = const <String>[],
    this.imagens = const <String>[],
  });

  final String numeroCrr;
  final String localFiscalizacao;
  final String municipioEstadoFiscalizacao;
  final String dataFiscalizacao;
  final String horaFiscalizacao;
  final String medidaAdministrativa;
  final String localPatio;
  final String placaGuincho;
  final String encarregado;
  final String observacao;
  final String matriculaAgente;
  final String placa;
  final String chassi;
  final String marca;
  final String modelo;
  final String cor;
  final String nomeCondutor;
  final String cpfCondutor;
  final String cnh;
  final String cnhEstrangeira;
  final List<String> aits;
  final List<String> enquadramentos;
  final List<String> imagens;

  Map<String, dynamic> toJson() {
    return <String, dynamic>{
      'numeroCrr': numeroCrr,
      'localFiscalizacao': localFiscalizacao,
      'municipioEstadoFiscalizacao': municipioEstadoFiscalizacao,
      'dataFiscalizacao': dataFiscalizacao,
      'horaFiscalizacao': horaFiscalizacao,
      'medidaAdministrativa': medidaAdministrativa,
      'localPatio': localPatio,
      'placaGuincho': placaGuincho,
      'encarregado': encarregado,
      'observacao': observacao,
      'matriculaAgente': matriculaAgente,
      'placa': placa,
      'chassi': chassi,
      'marca': marca,
      'modelo': modelo,
      'cor': cor,
      'nomeCondutor': nomeCondutor,
      'cpfCondutor': cpfCondutor,
      'cnh': cnh,
      'cnhEstrangeira': cnhEstrangeira,
      'aits': aits,
      'enquadramentos': enquadramentos,
      'imagens': imagens,
    };
  }
}
