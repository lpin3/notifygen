import 'package:flutter/material.dart';

import '../../auth/presentation/login_page.dart';
import '../../auth/services/auth_service.dart';
import '../../crr/models/crr_summary.dart';
import '../../crr/models/crr_draft.dart';
import '../../crr/presentation/crr_form_page.dart';
import '../../crr/presentation/crr_search_page.dart';
import '../../crr/services/crr_draft_service.dart';
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
  late final CrrDraftService _draftService;

  bool _busy = true;
  bool _syncing = false;
  String _deviceName = '';
  String _deviceId = '';
  bool _deviceActive = false;
  String _nextNumber = '';
  List<CrrSummary> _crrs = <CrrSummary>[];
  List<CrrDraft> _drafts = <CrrDraft>[];
  String _agentName = '';
  String _matricula = '';

  @override
  void initState() {
    super.initState();
    _draftService = CrrDraftService(storage: widget.authService.storage);
    _loadDashboard();
  }

  Future<void> _loadDashboard() async {
    setState(() => _busy = true);

    final matricula = await widget.authService.readMatricula();
    var agentName = await widget.authService.readAgentName();
    final drafts = await _draftService.loadDrafts();
    var deviceName = _deviceName;
    var deviceId = _deviceId;
    var deviceActive = _deviceActive;
    var nextNumber = _nextNumber;
    var crrs = _crrs;
    var networkWarning = false;

    try {
      final status = await widget.crrService.statusDispositivo();
      final dispositivo =
          status['dispositivo'] as Map<String, dynamic>? ?? <String, dynamic>{};
      final agente =
          status['agente'] as Map<String, dynamic>? ?? <String, dynamic>{};
      deviceName = dispositivo['nome'] as String? ?? 'Dispositivo';
      deviceId =
          dispositivo['device_id'] as String? ?? dispositivo['imei'] as String? ?? '';
      deviceActive = dispositivo['ativo'] as bool? ?? false;
      agentName = agente['nome'] as String? ?? agentName;
    } catch (error) {
      final message = error.toString().replaceFirst('Exception: ', '').toLowerCase();
      if (message.contains('desativado') ||
          message.contains('nao encontrado') ||
          message.contains('forbidden')) {
        await _handleUnauthorizedDevice();
        return;
      }
      networkWarning = true;
    }

    try {
      crrs = await widget.crrService.listarCrrs();
    } catch (_) {
      networkWarning = true;
    }

    try {
      nextNumber = await widget.crrService.obterProximoNumero();
    } catch (_) {
      networkWarning = true;
    }

    if (!mounted) {
      return;
    }

    setState(() {
      _agentName = agentName ?? '';
      _matricula = matricula ?? '';
      _deviceName = deviceName;
      _deviceId = deviceId;
      _deviceActive = deviceActive;
      _nextNumber = nextNumber;
      _crrs = crrs;
      _drafts = drafts;
      _busy = false;
    });

    if (networkWarning) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Alguns dados online não puderam ser atualizados. Os rascunhos locais continuam disponíveis.',
          ),
        ),
      );
    }
  }

  Future<void> _openNewCrr({CrrDraft? draft}) async {
    final changed = await Navigator.of(context).push<bool>(
      MaterialPageRoute<bool>(
        builder: (_) => CrrFormPage(
          authService: widget.authService,
          crrService: widget.crrService,
          draftService: _draftService,
          existingDraft: draft,
        ),
      ),
    );

    if (changed == true) {
      await _loadDashboard();
    }
  }

  Future<void> _openSearch() async {
    await Navigator.of(context).push<void>(
      MaterialPageRoute<void>(
        builder: (_) => CrrSearchPage(
          crrService: widget.crrService,
          authService: widget.authService,
        ),
      ),
    );
    await _loadDashboard();
  }

  Future<void> _syncDrafts() async {
    if (_drafts.isEmpty) {
      _showError('Não há rascunhos pendentes.');
      return;
    }

    setState(() => _syncing = true);
    try {
      final failed = await _draftService.syncDrafts(widget.crrService);
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            failed.isEmpty
                ? 'Todos os rascunhos foram sincronizados.'
                : '${failed.length} rascunho(s) permaneceram pendentes.',
          ),
        ),
      );
      await _loadDashboard();
    } catch (error) {
      _showError(error.toString());
    } finally {
      if (mounted) {
        setState(() => _syncing = false);
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

  Future<void> _handleUnauthorizedDevice() async {
    await widget.authService.logout();
    if (!mounted) {
      return;
    }

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text(
          'Este dispositivo não está mais autorizado. Faça login novamente ou solicite nova liberação.',
        ),
      ),
    );

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
    final colorScheme = Theme.of(context).colorScheme;
    final agentLabel = _agentName.isNotEmpty
        ? 'Agente $_agentName'
        : _matricula.isNotEmpty
        ? 'Agente $_matricula'
        : 'Sessão ativa';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Operação em campo'),
        actions: [
          IconButton(
            onPressed: _busy ? null : _loadDashboard,
            icon: const Icon(Icons.refresh),
            tooltip: 'Atualizar painel',
          ),
          IconButton(
            onPressed: _busy ? null : _logout,
            icon: const Icon(Icons.logout),
            tooltip: 'Encerrar sessão',
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadDashboard,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      colorScheme.primary,
                      colorScheme.secondary,
                    ],
                  ),
                  borderRadius: BorderRadius.circular(24),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      agentLabel,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            color: colorScheme.onPrimary,
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Acesso rápido para registrar atendimento, consultar CRRs e retomar rascunhos locais.',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: colorScheme.onPrimary,
                          ),
                    ),
                    const SizedBox(height: 16),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        _InfoPill(
                          label: _deviceActive ? 'Dispositivo ativo' : 'Aguardando liberação',
                          foregroundColor: colorScheme.onPrimary,
                          backgroundColor: colorScheme.onPrimary.withOpacity(0.14),
                        ),
                        _InfoPill(
                          label: _nextNumber.isEmpty
                              ? 'Numeração indisponível'
                              : 'Próximo CRR: $_nextNumber',
                          foregroundColor: colorScheme.onPrimary,
                          backgroundColor: colorScheme.onPrimary.withOpacity(0.14),
                        ),
                      ],
                    ),
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
                        'Ações principais',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w700,
                            ),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(
                            child: _ActionCard(
                              icon: Icons.note_add_outlined,
                              title: 'Novo CRR',
                              subtitle: 'Abrir fluxo guiado',
                              onTap: _busy ? null : () => _openNewCrr(),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: _ActionCard(
                              icon: Icons.search_outlined,
                              title: 'Consultar',
                              subtitle: 'Buscar ou revisar CRRs',
                              onTap: _busy ? null : _openSearch,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: _ActionCard(
                              icon: Icons.sync_outlined,
                              title: 'Sincronizar',
                              subtitle: _syncing
                                  ? 'Enviando rascunhos...'
                                  : '${_drafts.length} pendente(s)',
                              onTap: _busy || _syncing ? null : _syncDrafts,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: _ActionCard(
                              icon: Icons.badge_outlined,
                              title: 'Dispositivo',
                              subtitle: _deviceName.isEmpty
                                  ? 'Sem status'
                                  : _deviceName,
                              onTap: null,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
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
                        'Status de sincronização',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w700,
                            ),
                      ),
                      const SizedBox(height: 10),
                      Text(
                        _drafts.isEmpty
                            ? 'Sem rascunhos pendentes neste dispositivo.'
                            : 'Há ${_drafts.length} rascunho(s) aguardando envio. Você pode continuar preenchendo ou sincronizar quando a rede estabilizar.',
                      ),
                      if (_deviceId.isNotEmpty) ...[
                        const SizedBox(height: 12),
                        Text(
                          'ID do dispositivo: $_deviceId',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              if (_busy)
                const Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: CircularProgressIndicator()),
                )
              else ...[
                Text(
                  'Rascunhos locais',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const SizedBox(height: 8),
                if (_drafts.isEmpty)
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(18),
                      child: Text(
                        'Nenhum rascunho salvo. Use "Novo CRR" para iniciar um atendimento.',
                      ),
                    ),
                  ),
                ..._drafts.map(
                  (draft) => Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Card(
                      child: ListTile(
                        contentPadding: const EdgeInsets.all(16),
                        title: Text(
                          draft.payload.localFiscalizacao.isEmpty
                              ? 'Rascunho sem local definido'
                              : draft.payload.localFiscalizacao,
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                        subtitle: Text(
                          '${draft.payload.placa.isEmpty ? 'Sem placa' : draft.payload.placa} • ${draft.payload.dataFiscalizacao}\n${draft.lastError.isEmpty ? 'Aguardando sincronização' : draft.lastError}',
                        ),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: () => _openNewCrr(draft: draft),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  'Últimos CRRs',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const SizedBox(height: 8),
                if (_crrs.isEmpty)
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(18),
                      child: Text(
                        'Nenhum CRR recente disponível para esta matrícula.',
                      ),
                    ),
                  ),
                ..._crrs.map(
                  (crr) => Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Card(
                      child: ListTile(
                        contentPadding: const EdgeInsets.all(16),
                        title: Text(
                          crr.numeroCrr,
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                        subtitle: Text(
                          '${crr.placa} • ${crr.marca} ${crr.modelo}\n${crr.dataFiscalizacao}',
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

class _ActionCard extends StatelessWidget {
  const _ActionCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Ink(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: colorScheme.primary),
            const SizedBox(height: 16),
            Text(
              title,
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoPill extends StatelessWidget {
  const _InfoPill({
    required this.label,
    required this.foregroundColor,
    required this.backgroundColor,
  });

  final String label;
  final Color foregroundColor;
  final Color backgroundColor;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: foregroundColor,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
