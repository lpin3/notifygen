import 'package:flutter/material.dart';

import '../../auth/presentation/login_page.dart';
import '../../auth/services/auth_service.dart';
import '../../crr/models/crr_summary.dart';
import '../../crr/models/enquadramento_item.dart';
import '../../crr/services/crr_service.dart';

class HomePage extends StatefulWidget {
  const HomePage({
    required this.authService,
    required this.crrService,
    super.key,
  });

  final AuthService authService;
  final CrrService crrService;

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  bool _busy = false;
  String _statusText = 'Nenhuma consulta executada.';
  String _nextNumber = '';
  List<CrrSummary> _crrs = <CrrSummary>[];
  List<EnquadramentoItem> _enquadramentos = <EnquadramentoItem>[];
  String _matricula = '';

  @override
  void initState() {
    super.initState();
    _loadSessionInfo();
  }

  Future<void> _loadSessionInfo() async {
    final matricula = await widget.authService.readMatricula();
    if (!mounted) {
      return;
    }
    setState(() {
      _matricula = matricula ?? '';
    });
  }

  Future<void> _loadStatus() async {
    setState(() => _busy = true);
    try {
      final status = await widget.crrService.statusDispositivo();
      final dispositivo = status['dispositivo'] as Map<String, dynamic>? ?? <String, dynamic>{};
      if (!mounted) {
        return;
      }
      setState(() {
        _statusText =
            'Dispositivo: ${dispositivo['nome'] ?? ''}\nAtivo: ${dispositivo['ativo'] ?? ''}\nID do dispositivo: ${dispositivo['device_id'] ?? dispositivo['imei'] ?? ''}';
      });
    } catch (error) {
      _showError(error.toString());
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }

  Future<void> _loadCrrs() async {
    setState(() => _busy = true);
    try {
      final crrs = await widget.crrService.listarCrrs();
      if (!mounted) {
        return;
      }
      setState(() {
        _crrs = crrs;
      });
    } catch (error) {
      _showError(error.toString());
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }

  Future<void> _loadEnquadramentos() async {
    setState(() => _busy = true);
    try {
      final itens = await widget.crrService.listarEnquadramentos();
      if (!mounted) {
        return;
      }
      setState(() {
        _enquadramentos = itens;
      });
    } catch (error) {
      _showError(error.toString());
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }

  Future<void> _loadNextNumber() async {
    setState(() => _busy = true);
    try {
      final numero = await widget.crrService.obterProximoNumero();
      if (!mounted) {
        return;
      }
      setState(() {
        _nextNumber = numero;
      });
    } catch (error) {
      _showError(error.toString());
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }

  Future<void> _logout() async {
    await widget.authService.logout();
    if (!mounted) {
      return;
    }

    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute<void>(
        builder: (_) => LoginPage(
          storage: widget.authService.storage,
          apiClient: widget.authService.apiClient,
        ),
      ),
      (route) => false,
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
    return Scaffold(
      appBar: AppBar(
        title: const Text('Painel Mobile'),
        actions: [
          IconButton(
            onPressed: _busy ? null : _logout,
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(
                    _matricula.isEmpty
                        ? 'Sessao autenticada.'
                        : 'Sessao autenticada para a matricula $_matricula.',
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  FilledButton(
                    onPressed: _busy ? null : _loadStatus,
                    child: const Text('Status'),
                  ),
                  FilledButton(
                    onPressed: _busy ? null : _loadCrrs,
                    child: const Text('CRRs'),
                  ),
                  FilledButton(
                    onPressed: _busy ? null : _loadEnquadramentos,
                    child: const Text('Enquadramentos'),
                  ),
                  FilledButton(
                    onPressed: _busy ? null : _loadNextNumber,
                    child: const Text('Proximo CRR'),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              if (_busy) const Center(child: CircularProgressIndicator()),
              if (!_busy) ...[
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Text(
                      _nextNumber.isEmpty
                          ? _statusText
                          : '$_statusText\n\nProximo numero sugerido: $_nextNumber',
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                if (_crrs.isNotEmpty) ...[
                  const Text(
                    'Ultimos CRRs',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  ..._crrs.map(
                    (crr) => Card(
                      child: ListTile(
                        title: Text(crr.numeroCrr),
                        subtitle: Text(
                          '${crr.placa} | ${crr.marca} ${crr.modelo}\n${crr.dataFiscalizacao}',
                        ),
                        trailing: Text(crr.status),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                ],
                if (_enquadramentos.isNotEmpty) ...[
                  const Text(
                    'Enquadramentos',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  ..._enquadramentos.take(10).map(
                    (item) => Card(
                      child: ListTile(
                        title: Text(item.codigo),
                        subtitle: Text(item.descricaoInfracao),
                      ),
                    ),
                  ),
                ],
              ],
            ],
          ),
        ),
      ),
    );
  }
}
