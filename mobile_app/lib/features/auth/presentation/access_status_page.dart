import 'package:flutter/material.dart';

import '../models/access_request_result.dart';

class AccessStatusPage extends StatefulWidget {
  const AccessStatusPage({
    required this.initialResult,
    required this.onRefreshStatus,
    super.key,
  });

  final AccessRequestResult initialResult;
  final Future<AccessRequestResult> Function() onRefreshStatus;

  @override
  State<AccessStatusPage> createState() => _AccessStatusPageState();
}

class _AccessStatusPageState extends State<AccessStatusPage> {
  late AccessRequestResult _result;
  bool _busy = false;

  @override
  void initState() {
    super.initState();
    _result = widget.initialResult;
  }

  Future<void> _refreshStatus() async {
    setState(() => _busy = true);
    try {
      final updated = await widget.onRefreshStatus();
      if (!mounted) {
        return;
      }

      if (updated.isApproved) {
        Navigator.of(context).pop(updated);
        return;
      }

      setState(() => _result = updated);
    } catch (error) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(error.toString().replaceFirst('Exception: ', '')),
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isBlocked = _result.isBlocked;
    final icon = isBlocked ? Icons.block_outlined : Icons.hourglass_top_outlined;
    final headerColor = isBlocked ? colorScheme.error : colorScheme.secondary;
    final title = isBlocked ? 'Dispositivo bloqueado' : 'Liberação pendente';
    final description = isBlocked
        ? (_result.blockedReason.isEmpty
            ? 'Este dispositivo não está autorizado para operar no app.'
            : _result.blockedReason)
        : 'A solicitação foi registrada com sucesso. Aguarde a aprovação administrativa para concluir o acesso.';

    return Scaffold(
      appBar: AppBar(title: const Text('Status do acesso')),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: headerColor.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(24),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(icon, color: headerColor, size: 32),
                    const SizedBox(height: 16),
                    Text(
                      title,
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            color: headerColor,
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Text(description),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Solicitação atual',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w700,
                            ),
                      ),
                      const SizedBox(height: 12),
                      _InfoRow(label: 'Agente', value: _result.agentName),
                      _InfoRow(label: 'Matrícula', value: _result.agentMatricula),
                      _InfoRow(label: 'Dispositivo', value: _result.deviceName),
                      _InfoRow(label: 'ID', value: _result.deviceId),
                      if ((_result.requestedAt ?? '').isNotEmpty)
                        _InfoRow(label: 'Solicitado em', value: _result.requestedAt!),
                      if ((_result.approvedAt ?? '').isNotEmpty)
                        _InfoRow(label: 'Aprovado em', value: _result.approvedAt!),
                      const SizedBox(height: 8),
                      Text(
                        _result.message,
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ),
              const Spacer(),
              FilledButton.icon(
                onPressed: _busy ? null : _refreshStatus,
                icon: const Icon(Icons.refresh),
                label: Text(_busy ? 'Atualizando...' : 'Atualizar status'),
              ),
              const SizedBox(height: 8),
              OutlinedButton(
                onPressed: _busy ? null : () => Navigator.of(context).pop(),
                child: const Text('Voltar e alterar credenciais'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({
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
            width: 96,
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
          ),
          Expanded(
            child: Text(value.isEmpty ? 'Não informado' : value),
          ),
        ],
      ),
    );
  }
}
