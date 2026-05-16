import 'package:flutter/material.dart';

import '../../../core/widgets/app_logo.dart';
import '../../auth/presentation/agent_profile_page.dart';
import '../../auth/services/auth_service.dart';
import '../../crr/models/crr_draft.dart';
import '../../crr/models/crr_summary.dart';
import '../../crr/presentation/crr_form_page.dart';
import '../../crr/presentation/crr_search_page.dart';
import '../../crr/services/crr_draft_service.dart';
import '../../crr/services/crr_service.dart';
import '../../splash/presentation/splash_page.dart';

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
  bool _deviceActivated = false;
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

    var matricula = await widget.authService.readMatricula();
    var agentName = await widget.authService.readAgentName();
    final drafts = await _draftService.loadDrafts();
    var deviceName = _deviceName;
    var deviceId = _deviceId;
    var deviceActive = _deviceActive;
    var deviceActivated = _deviceActivated;
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
      deviceActivated = dispositivo['ativado'] as bool? ?? false;

      final agenteMatricula = (agente['matricula'] as String? ?? '').trim();
      final agenteNome = (agente['nome'] as String? ?? '').trim();
      final sessionMatricula = (matricula ?? '').trim();

      if (agenteMatricula.isNotEmpty &&
          (sessionMatricula.isEmpty || agenteMatricula == sessionMatricula)) {
        matricula = agenteMatricula;
        if (agenteNome.isNotEmpty) {
          agentName = agenteNome;
        }
        await widget.authService.persistSessionAgent(
          agentName: agenteNome.isNotEmpty ? agenteNome : null,
          matricula: agenteMatricula,
        );
      }
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
      _deviceActivated = deviceActivated;
      _nextNumber = nextNumber;
      _crrs = crrs;
      _drafts = drafts;
      _busy = false;
    });

    if (networkWarning) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Alguns dados online nao puderam ser atualizados. Os rascunhos locais continuam disponiveis.',
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

  Future<void> _openProfile() async {
    final changed = await Navigator.of(context).push<bool>(
      MaterialPageRoute<bool>(
        builder: (_) => AgentProfilePage(
          authService: widget.authService,
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
      _showError('Nao ha rascunhos pendentes.');
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
        builder: (_) => SplashPage(
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
          'Este dispositivo nao esta mais autorizado. Faca login novamente ou solicite nova liberacao.',
        ),
      ),
    );

    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute<void>(
        builder: (_) => SplashPage(
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

  String get _displayName {
    if (_agentName.isNotEmpty) {
      return _agentName;
    }
    if (_matricula.isNotEmpty) {
      return 'Matricula $_matricula';
    }
    return 'Agente';
  }

  bool get _deviceAuthorized => _deviceActive && _deviceActivated;

  String get _profileInitials {
    final source = _agentName.isNotEmpty ? _agentName : _matricula;
    if (source.isEmpty) {
      return 'AG';
    }
    final parts = source.trim().split(RegExp(r'\s+'));
    if (parts.length >= 2) {
      return '${parts.first[0]}${parts[1][0]}'.toUpperCase();
    }
    return source.substring(0, source.length >= 2 ? 2 : 1).toUpperCase();
  }

  Future<void> _showOperationalStatus() async {
    await showDialog<void>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Status operacional'),
          content: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                _DialogStatusRow(
                  icon: Icons.sync_problem_outlined,
                  label: 'Sincronizacao',
                  value: _drafts.isEmpty
                      ? 'Nenhum rascunho pendente'
                      : '${_drafts.length} rascunho(s) pendente(s)',
                ),
                const SizedBox(height: 16),
                _DialogStatusRow(
                  icon: Icons.tag_outlined,
                  label: 'Proximo CRR',
                  value: _nextNumber.isEmpty
                      ? 'Numeracao indisponivel no momento'
                      : _nextNumber,
                ),
                const SizedBox(height: 16),
                _DialogStatusRow(
                  icon: Icons.smartphone_rounded,
                  label: 'Dispositivo',
                  value: _deviceName.isEmpty
                      ? 'Sem status disponivel'
                      : _deviceName,
                ),
                const SizedBox(height: 16),
                _DialogStatusRow(
                  icon: _deviceAuthorized
                      ? Icons.verified_user_outlined
                      : Icons.phonelink_lock_outlined,
                  label: 'Autorizacao',
                  value: _deviceAuthorized
                      ? 'Dispositivo autorizado'
                      : 'Aguardando liberacao',
                ),
                if (_deviceId.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  _DialogStatusRow(
                    icon: Icons.fingerprint_rounded,
                    label: 'Identificador',
                    value: _deviceId,
                  ),
                ],
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Fechar'),
            ),
            if (_drafts.isNotEmpty && !_syncing)
              FilledButton(
                onPressed: () {
                  Navigator.of(context).pop();
                  _syncDrafts();
                },
                child: const Text('Sincronizar'),
              ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        leadingWidth: 56,
        leading: Padding(
          padding: const EdgeInsets.only(left: 8),
          child: IconButton(
            onPressed: _busy ? null : _openProfile,
            tooltip: 'Meu perfil',
            icon: _AppBarProfileAvatar(initials: _profileInitials),
          ),
        ),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _displayName,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            if (_matricula.isNotEmpty)
              Text(
                'Mat. $_matricula',
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                      fontWeight: FontWeight.w600,
                    ),
              ),
          ],
        ),
        actions: [
          IconButton(
            onPressed: _busy ? null : _showOperationalStatus,
            icon: _OperationalStatusIcon(
              deviceAuthorized: _deviceAuthorized,
              pendingDrafts: _drafts.length,
            ),
            tooltip: 'Status operacional',
          ),
          IconButton(
            onPressed: _busy ? null : _loadDashboard,
            icon: const Icon(Icons.refresh_rounded),
            tooltip: 'Atualizar painel',
          ),
          IconButton(
            onPressed: _busy ? null : _logout,
            icon: const Icon(Icons.logout_rounded),
            tooltip: 'Encerrar sessao',
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _busy ? null : () => _openNewCrr(),
        icon: const Icon(Icons.add_task_rounded),
        label: const Text('Novo CRR'),
      ),
      body: RefreshIndicator(
        onRefresh: _loadDashboard,
        child: CustomScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          slivers: [
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 96),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 18,
                      ),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [
                            colorScheme.primary,
                            colorScheme.secondary,
                          ],
                        ),
                        borderRadius: BorderRadius.circular(24),
                      ),
                      child: Row(
                        children: [
                          Expanded(
                            child: Text(
                              'Atendimentos, rascunhos offline e consulta de CRRs em um so lugar.',
                              style: Theme.of(context)
                                  .textTheme
                                  .bodyMedium
                                  ?.copyWith(
                                    color: colorScheme.onPrimary,
                                    height: 1.35,
                                  ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          const AppLogo(size: 52, showWordmark: false),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: _MetricCard(
                            icon: Icons.description_outlined,
                            label: 'Rascunhos',
                            value: '${_drafts.length}',
                            hint: _drafts.isEmpty
                                ? 'Sem pendencias'
                                : 'Aguardando envio',
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _MetricCard(
                            icon: Icons.pin_outlined,
                            label: 'Proximo CRR',
                            value: _nextNumber.isEmpty ? '--' : _nextNumber,
                            hint: 'Para novo registro',
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(18),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const _SectionHeader(
                              title: 'Atalhos rapidos',
                              subtitle:
                                  'Toque para consultar ou enviar rascunhos pendentes.',
                            ),
                            const SizedBox(height: 8),
                            _ShortcutListTile(
                              icon: Icons.search_rounded,
                              title: 'Consultar CRRs',
                              onTap: _busy ? null : _openSearch,
                            ),
                            const Divider(height: 1),
                            _ShortcutListTile(
                              icon: Icons.sync_rounded,
                              title: 'Sincronizar rascunhos',
                              subtitle: _syncing
                                  ? 'Enviando rascunhos...'
                                  : _drafts.isEmpty
                                      ? 'Nenhum pendente'
                                      : null,
                              badgeCount:
                                  _drafts.isEmpty ? null : _drafts.length,
                              showProgress: _syncing,
                              onTap: _busy || _syncing || _drafts.isEmpty
                                  ? null
                                  : _syncDrafts,
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    if (_busy)
                      const Padding(
                        padding: EdgeInsets.symmetric(vertical: 48),
                        child: Center(child: CircularProgressIndicator()),
                      )
                    else ...[
                      const _SectionHeader(
                        title: 'Rascunhos locais',
                        subtitle: 'Continue exatamente de onde parou, mesmo sem rede.',
                      ),
                      const SizedBox(height: 12),
                      if (_drafts.isEmpty)
                        const _EmptyStateCard(
                          icon: Icons.drafts_outlined,
                          title: 'Nenhum rascunho salvo',
                          description:
                              'Use o botao "Novo CRR" para iniciar um atendimento e continuar depois se necessario.',
                        ),
                      ..._drafts.map(
                        (draft) => Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: Card(
                            child: ListTile(
                              contentPadding: const EdgeInsets.all(16),
                              leading: CircleAvatar(
                                backgroundColor: colorScheme.primaryContainer,
                                foregroundColor: colorScheme.onPrimaryContainer,
                                child: const Icon(Icons.description_outlined),
                              ),
                              title: Text(
                                draft.payload.localFiscalizacao.isEmpty
                                    ? 'Rascunho sem local definido'
                                    : draft.payload.localFiscalizacao,
                                style: const TextStyle(fontWeight: FontWeight.w700),
                              ),
                              subtitle: Padding(
                                padding: const EdgeInsets.only(top: 6),
                                child: Text(
                                  '${draft.payload.placa.isEmpty ? 'Sem placa' : draft.payload.placa} • ${draft.payload.dataFiscalizacao}\n${draft.lastError.isEmpty ? 'Aguardando sincronizacao' : draft.lastError}',
                                ),
                              ),
                              trailing: const Icon(Icons.chevron_right_rounded),
                              onTap: () => _openNewCrr(draft: draft),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 20),
                      const _SectionHeader(
                        title: 'Ultimos CRRs',
                        subtitle: 'Acompanhe rapidamente os registros mais recentes da sua matricula.',
                      ),
                      const SizedBox(height: 12),
                      if (_crrs.isEmpty)
                        const _EmptyStateCard(
                          icon: Icons.inbox_outlined,
                          title: 'Nenhum CRR recente disponivel',
                          description:
                              'Assim que houver registros vinculados a esta matricula, eles aparecerao aqui.',
                        ),
                      ..._crrs.map(
                        (crr) => Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: Card(
                            child: ListTile(
                              contentPadding: const EdgeInsets.all(16),
                              leading: CircleAvatar(
                                backgroundColor: colorScheme.secondaryContainer,
                                foregroundColor: colorScheme.onSecondaryContainer,
                                child: const Icon(Icons.assignment_outlined),
                              ),
                              title: Text(
                                crr.numeroCrr,
                                style: const TextStyle(fontWeight: FontWeight.w700),
                              ),
                              subtitle: Padding(
                                padding: const EdgeInsets.only(top: 6),
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
            ),
          ],
        ),
      ),
    );
  }
}

class _AppBarProfileAvatar extends StatelessWidget {
  const _AppBarProfileAvatar({required this.initials});

  final String initials;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return CircleAvatar(
      backgroundColor: colorScheme.primaryContainer,
      foregroundColor: colorScheme.onPrimaryContainer,
      child: Text(
        initials,
        style: const TextStyle(
          fontWeight: FontWeight.w800,
          fontSize: 14,
        ),
      ),
    );
  }
}

class _OperationalStatusIcon extends StatelessWidget {
  const _OperationalStatusIcon({
    required this.deviceAuthorized,
    required this.pendingDrafts,
  });

  final bool deviceAuthorized;
  final int pendingDrafts;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final statusColor =
        deviceAuthorized ? const Color(0xFF2E7D32) : colorScheme.tertiary;

    final icon = pendingDrafts > 0
        ? Badge(
            label: Text('$pendingDrafts'),
            child: const Icon(Icons.insights_outlined),
          )
        : const Icon(Icons.insights_outlined);

    return Stack(
      clipBehavior: Clip.none,
      children: [
        icon,
        Positioned(
          left: 0,
          bottom: 0,
          child: Container(
            width: 10,
            height: 10,
            decoration: BoxDecoration(
              color: statusColor,
              shape: BoxShape.circle,
              border: Border.all(color: colorScheme.surface, width: 1.5),
            ),
          ),
        ),
      ],
    );
  }
}

class _DialogStatusRow extends StatelessWidget {
  const _DialogStatusRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: colorScheme.surfaceContainerHighest,
            borderRadius: BorderRadius.circular(14),
          ),
          child: Icon(icon, color: colorScheme.primary, size: 20),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
              ),
              const SizedBox(height: 4),
              Text(
                value,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _ShortcutListTile extends StatelessWidget {
  const _ShortcutListTile({
    required this.icon,
    required this.title,
    this.subtitle,
    this.badgeCount,
    this.showProgress = false,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String? subtitle;
  final int? badgeCount;
  final bool showProgress;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final enabled = onTap != null;

    Widget? trailing;
    if (showProgress) {
      trailing = SizedBox(
        width: 24,
        height: 24,
        child: CircularProgressIndicator(
          strokeWidth: 2,
          color: colorScheme.primary,
        ),
      );
    } else if (badgeCount != null && badgeCount! > 0) {
      trailing = Badge(
        label: Text('$badgeCount'),
        child: const Icon(Icons.chevron_right_rounded),
      );
    } else if (enabled) {
      trailing = const Icon(Icons.chevron_right_rounded);
    }

    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
      enabled: enabled,
      leading: CircleAvatar(
        backgroundColor: enabled
            ? colorScheme.primaryContainer
            : colorScheme.surfaceContainerHighest,
        foregroundColor: enabled
            ? colorScheme.onPrimaryContainer
            : colorScheme.onSurfaceVariant,
        child: Icon(icon),
      ),
      title: Text(
        title,
        style: TextStyle(
          fontWeight: FontWeight.w700,
          color: enabled ? null : colorScheme.onSurfaceVariant,
        ),
      ),
      subtitle: subtitle == null
          ? null
          : Text(
              subtitle!,
              style: TextStyle(color: colorScheme.onSurfaceVariant),
            ),
      trailing: trailing,
      onTap: onTap,
    );
  }
}

class _MetricCard extends StatelessWidget {
  const _MetricCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.hint,
  });

  final IconData icon;
  final String label;
  final String value;
  final String hint;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: colorScheme.primary),
            const SizedBox(height: 12),
            Text(
              label,
              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              hint,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({
    required this.title,
    required this.subtitle,
  });

  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w800,
              ),
        ),
        const SizedBox(height: 4),
        Text(
          subtitle,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
        ),
      ],
    );
  }
}

class _EmptyStateCard extends StatelessWidget {
  const _EmptyStateCard({
    required this.icon,
    required this.title,
    required this.description,
  });

  final IconData icon;
  final String title;
  final String description;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 46,
              height: 46,
              decoration: BoxDecoration(
                color: colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(icon, color: colorScheme.primary),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    description,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: colorScheme.onSurfaceVariant,
                        ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

