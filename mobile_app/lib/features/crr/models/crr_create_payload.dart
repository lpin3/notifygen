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
    this.veiculoSemIdentificacao = false,
    this.situacaoEntrega = '',
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
  final bool veiculoSemIdentificacao;
  final String situacaoEntrega;

  factory CrrCreatePayload.fromJson(Map<String, dynamic> json) {
    List<String> _readStringList(String key) {
      return (json[key] as List<dynamic>? ?? <dynamic>[])
          .map((item) => item.toString())
          .where((item) => item.isNotEmpty)
          .toList();
    }

    return CrrCreatePayload(
      numeroCrr: json['numeroCrr'] as String? ?? '',
      localFiscalizacao: json['localFiscalizacao'] as String? ?? '',
      municipioEstadoFiscalizacao:
          json['municipioEstadoFiscalizacao'] as String? ?? '',
      dataFiscalizacao: json['dataFiscalizacao'] as String? ?? '',
      horaFiscalizacao: json['horaFiscalizacao'] as String? ?? '',
      medidaAdministrativa: json['medidaAdministrativa'] as String? ??
          'Remocao do veiculo ao Deposito',
      localPatio: json['localPatio'] as String? ?? '',
      placaGuincho: json['placaGuincho'] as String? ?? '',
      encarregado: json['encarregado'] as String? ?? '',
      observacao: json['observacao'] as String? ?? '',
      matriculaAgente: json['matriculaAgente'] as String? ?? '',
      placa: json['placa'] as String? ?? '',
      chassi: json['chassi'] as String? ?? '',
      marca: json['marca'] as String? ?? '',
      modelo: json['modelo'] as String? ?? '',
      cor: json['cor'] as String? ?? '',
      nomeCondutor: json['nomeCondutor'] as String? ?? '',
      cpfCondutor: json['cpfCondutor'] as String? ?? '',
      cnh: json['cnh'] as String? ?? '',
      cnhEstrangeira: json['cnhEstrangeira'] as String? ?? '',
      aits: _readStringList('aits'),
      enquadramentos: _readStringList('enquadramentos'),
      imagens: _readStringList('imagens'),
      veiculoSemIdentificacao:
          json['veiculoSemIdentificacao'] as bool? ?? false,
      situacaoEntrega: json['situacaoEntrega'] as String? ?? '',
    );
  }

  CrrCreatePayload copyWith({
    String? numeroCrr,
    String? localFiscalizacao,
    String? municipioEstadoFiscalizacao,
    String? dataFiscalizacao,
    String? horaFiscalizacao,
    String? medidaAdministrativa,
    String? localPatio,
    String? placaGuincho,
    String? encarregado,
    String? observacao,
    String? matriculaAgente,
    String? placa,
    String? chassi,
    String? marca,
    String? modelo,
    String? cor,
    String? nomeCondutor,
    String? cpfCondutor,
    String? cnh,
    String? cnhEstrangeira,
    List<String>? aits,
    List<String>? enquadramentos,
    List<String>? imagens,
    bool? veiculoSemIdentificacao,
    String? situacaoEntrega,
  }) {
    return CrrCreatePayload(
      numeroCrr: numeroCrr ?? this.numeroCrr,
      localFiscalizacao: localFiscalizacao ?? this.localFiscalizacao,
      municipioEstadoFiscalizacao:
          municipioEstadoFiscalizacao ?? this.municipioEstadoFiscalizacao,
      dataFiscalizacao: dataFiscalizacao ?? this.dataFiscalizacao,
      horaFiscalizacao: horaFiscalizacao ?? this.horaFiscalizacao,
      medidaAdministrativa:
          medidaAdministrativa ?? this.medidaAdministrativa,
      localPatio: localPatio ?? this.localPatio,
      placaGuincho: placaGuincho ?? this.placaGuincho,
      encarregado: encarregado ?? this.encarregado,
      observacao: observacao ?? this.observacao,
      matriculaAgente: matriculaAgente ?? this.matriculaAgente,
      placa: placa ?? this.placa,
      chassi: chassi ?? this.chassi,
      marca: marca ?? this.marca,
      modelo: modelo ?? this.modelo,
      cor: cor ?? this.cor,
      nomeCondutor: nomeCondutor ?? this.nomeCondutor,
      cpfCondutor: cpfCondutor ?? this.cpfCondutor,
      cnh: cnh ?? this.cnh,
      cnhEstrangeira: cnhEstrangeira ?? this.cnhEstrangeira,
      aits: aits ?? this.aits,
      enquadramentos: enquadramentos ?? this.enquadramentos,
      imagens: imagens ?? this.imagens,
      veiculoSemIdentificacao:
          veiculoSemIdentificacao ?? this.veiculoSemIdentificacao,
      situacaoEntrega: situacaoEntrega ?? this.situacaoEntrega,
    );
  }

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
      'veiculoSemIdentificacao': veiculoSemIdentificacao,
      'situacaoEntrega': situacaoEntrega,
    };
  }
}
