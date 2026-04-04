class EnquadramentoItem {
  EnquadramentoItem({
    required this.codigo,
    required this.amparoLegal,
    required this.descricaoInfracao,
  });

  final String codigo;
  final String amparoLegal;
  final String descricaoInfracao;

  factory EnquadramentoItem.fromJson(Map<String, dynamic> json) {
    return EnquadramentoItem(
      codigo: json['codigo'] as String? ?? '',
      amparoLegal: json['amparo_legal'] as String? ?? '',
      descricaoInfracao: json['descricao_infracao'] as String? ?? '',
    );
  }
}
