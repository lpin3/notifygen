import 'package:flutter/material.dart';

import '../../auth/services/auth_service.dart';
import '../models/crr_summary.dart';
import '../services/crr_service.dart';

class CrrSearchPage extends StatefulWidget {
  const CrrSearchPage({
    required this.crrService,
    required this.authService,
    super.key,
  });

  final CrrService crrService;
  final AuthService authService;

  @override
  State<CrrSearchPage> createState() => _CrrSearchPageState();
}

class _CrrSearchPageState extends State<CrrSearchPage> {
  final _numeroController = TextEditingController();
  final _placaController = TextEditingController();
  final _marcaController = TextEditingController();
  final _modeloController = TextEditingController();
  final _dataController = TextEditingController();

  bool _busy = true;
  bool _hasSearch = false;
  String _matricula = '';
  List<CrrSummary> _recent = <CrrSummary>[];
  List<CrrSummary> _results = <CrrSummary>[];

  @override
  void initState() {
    super.initState();
    _bootstrap();
  }

  @override
  void dispose() {
    _numeroController.dispose();
    _placaController.dispose();
    _marcaController.dispose();
    _modeloController.dispose();
    _dataController.dispose();
    super.dispose();
  }

  Future<void> _bootstrap() async {
    final matricula = await widget.authService.readMatricula() ?? '';
    setState(() => _matricula = matricula);
    await _loadRecent();
  }

  Future<void> _loadRecent() async {
    setState(() => _busy = true);
    try {
      final items = await widget.crrService.listarCrrs();
      if (!mounted) {
        return;
      }
      setState(() {
        _recent = items;
      });
    } catch (error) {
      _showError(error.toString());
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }

  Future<void> _search() async {
    if (_numeroController.text.trim().isEmpty &&
        _placaController.text.trim().isEmpty &&
        _marcaController.text.trim().isEmpty &&
        _modeloController.text.trim().isEmpty &&
        _dataController.text.trim().isEmpty) {
      _showError('Informe ao menos um filtro para buscar.');
      return;
    }

    setState(() => _busy = true);
    try {
      final items = await widget.crrService.buscarCrrs(
        numeroCrr: _numeroController.text,
        placa: _placaController.text,
        marca: _marcaController.text,
        modelo: _modeloController.text,
        data: _dataController.text,
      );
      if (!mounted) {
        return;
      }
      setState(() {
        _hasSearch = true;
        _results = items;
      });
    } catch (error) {
      _showError(error.toString());
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }

  void _clearFilters() {
    _numeroController.clear();
    _placaController.clear();
    _marcaController.clear();
    _modeloController.clear();
    _dataController.clear();
    setState(() {
      _hasSearch = false;
      _results = <CrrSummary>[];
    });
  }

  void _openDetails(CrrSummary crr) {
    showModalBottomSheet<void>(
      context: context,
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  crr.numeroCrr,
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const SizedBox(height: 16),
                _DetailRow(label: 'Placa', value: crr.placa),
                _DetailRow(label: 'Marca', value: crr.marca),
                _DetailRow(label: 'Modelo', value: crr.modelo),
                _DetailRow(label: 'Status', value: crr.status),
                _DetailRow(label: 'Data', value: crr.dataFiscalizacao),
                const SizedBox(height: 16),
                Text(
                  'A API mobile atual fornece apenas resumo nesta consulta. Este layout já organiza o acesso para futura expansão do detalhe completo.',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _showError(String message) {
    if (!mounted) {
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message.replaceFirst('Exception: ', ''))),
    );
  }

  @override
  Widget build(BuildContext context) {
    final displayedItems = _hasSearch ? _results : _recent;

    return Scaffold(
      appBar: AppBar(title: const Text('Consultar CRRs')),
      body: RefreshIndicator(
        onRefresh: _loadRecent,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Busca operacional',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      _matricula.isEmpty
                          ? 'Consulte seus últimos CRRs ou faça uma busca por filtros.'
                          : 'Sessão ativa para matrícula $_matricula. Seus últimos CRRs aparecem abaixo quando não há busca ativa.',
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _numeroController,
                      decoration: const InputDecoration(
                        labelText: 'Número do CRR',
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _placaController,
                            textCapitalization: TextCapitalization.characters,
                            decoration: const InputDecoration(labelText: 'Placa'),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: TextField(
                            controller: _dataController,
                            decoration: const InputDecoration(
                              labelText: 'Data (AAAA-MM-DD)',
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _marcaController,
                            decoration: const InputDecoration(labelText: 'Marca'),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: TextField(
                            controller: _modeloController,
                            decoration: const InputDecoration(labelText: 'Modelo'),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    FilledButton.icon(
                      onPressed: _busy ? null : _search,
                      icon: const Icon(Icons.search),
                      label: const Text('Buscar'),
                    ),
                    const SizedBox(height: 8),
                    OutlinedButton(
                      onPressed: _busy ? null : _clearFilters,
                      child: const Text('Limpar filtros'),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'A busca consulta a base geral disponível na API mobile atual.',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              _hasSearch ? 'Resultados da busca' : 'Meus últimos CRRs',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 8),
            if (_busy) ...[
              const Padding(
                padding: EdgeInsets.all(24),
                child: Center(child: CircularProgressIndicator()),
              ),
            ] else if (displayedItems.isEmpty) ...[
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Text(
                    _hasSearch
                        ? 'Nenhum CRR encontrado com os filtros informados.'
                        : 'Nenhum CRR recente disponível para esta sessão.',
                  ),
                ),
              ),
            ] else ...[
              ...displayedItems.map(
                (crr) => Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: Card(
                    child: ListTile(
                      contentPadding: const EdgeInsets.all(16),
                      onTap: () => _openDetails(crr),
                      title: Text(
                        crr.numeroCrr,
                        style: const TextStyle(fontWeight: FontWeight.w700),
                      ),
                      subtitle: Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: Text(
                          '${crr.placa} • ${crr.marca} ${crr.modelo}\n${crr.dataFiscalizacao}',
                        ),
                      ),
                      trailing: Chip(label: Text(crr.status)),
                    ),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow({
    required this.label,
    required this.value,
  });

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 72,
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
          ),
          Expanded(child: Text(value.isEmpty ? 'Não informado' : value)),
        ],
      ),
    );
  }
}
