class CrrSummary {
  CrrSummary({
    required this.id,
    required this.numeroCrr,
    required this.placa,
    required this.marca,
    required this.modelo,
    required this.status,
    required this.dataFiscalizacao,
  });

  final int id;
  final String numeroCrr;
  final String placa;
  final String marca;
  final String modelo;
  final String status;
  final String dataFiscalizacao;

  factory CrrSummary.fromJson(Map<String, dynamic> json) {
    return CrrSummary(
      id: json['id'] as int? ?? 0,
      numeroCrr: json['numeroCrr'] as String? ?? '',
      placa: json['placa'] as String? ?? '',
      marca: json['marca'] as String? ?? '',
      modelo: json['modelo'] as String? ?? '',
      status: json['status'] as String? ?? '',
      dataFiscalizacao: json['dataFiscalizacao'] as String? ?? '',
    );
  }
}
