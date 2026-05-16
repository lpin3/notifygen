import 'package:flutter/material.dart';

import '../../../core/widgets/app_logo.dart';
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

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final agentLabel = _agentName.isNotEmpty
        ? _agentName
        : _matricula.isNotEmpty
            ? _matricula
            : 'Sessao ativa';
    final greeting = _agentName.isNotEmpty || _matricula.isNotEmpty
        ? 'Ola, $agentLabel'
        : 'Painel operacional';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Operacao em campo'),
        actions: [
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
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [
                            colorScheme.primary,
                            colorScheme.secondary,
                          ],
                        ),
                        borderRadius: BorderRadius.circular(28),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      greeting,
                                      style: Theme.of(context)
                                          .textTheme
                                          .headlineSmall
                                          ?.copyWith(
                                            color: colorScheme.onPrimary,
                                            fontWeight: FontWeight.w800,
                                          ),
                                    ),
                                    const SizedBox(height: 8),
                                    Text(
                                      'Gerencie atendimentos, acompanhe rascunhos offline e consulte os CRRs mais recentes em um unico painel.',
                                      style: Theme.of(context)
                                          .textTheme
                                          .bodyMedium
                                          ?.copyWith(
                                            color: colorScheme.onPrimary,
                                          ),
                                    ),
                                  ],
                                ),
                              ),
                              const SizedBox(width: 16),
                              const AppLogo(size: 64, showWordmark: false),
                            ],
                          ),
                          const SizedBox(height: 18),
                          Wrap(
                            spacing: 8,
                            runSpacing: 8,
                            children: [
                              _InfoPill(
                                label: _deviceActive
                                    ? 'Dispositivo ativo'
                                    : 'Aguardando liberacao',
                                foregroundColor: colorScheme.onPrimary,
                                backgroundColor:
                                    colorScheme.onPrimary.withOpacity(0.14),
                              ),
                              _InfoPill(
                                label: _nextNumber.isEmpty
                                    ? 'Numeracao indisponivel'
                                    : 'Proximo CRR: $_nextNumber',
                                foregroundColor: colorScheme.onPrimary,
                                backgroundColor:
                                    colorScheme.onPrimary.withOpacity(0.14),
                              ),
                              if (_matricula.isNotEmpty)
                                _InfoPill(
                                  label: 'Matricula $_matricula',
                                  foregroundColor: colorScheme.onPrimary,
                                  backgroundColor:
                                      colorScheme.onPrimary.withOpacity(0.14),
                                ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    Wrap(
                      spacing: 12,
                      runSpacing: 12,
                      children: [
                        SizedBox(
                          width: 180,
                          child: _MetricCard(
                            icon: Icons.description_outlined,
                            label: 'Rascunhos',
                            value: '${_drafts.length}',
                            hint: _drafts.isEmpty ? 'Sem pendencias' : 'Aguardando envio',
                          ),
                        ),
                        SizedBox(
                          width: 180,
                          child: _MetricCard(
                            icon: Icons.pin_outlined,
                            label: 'Proximo numero',
                            value: _nextNumber.isEmpty ? '--' : _nextNumber,
                            hint: 'Disponivel para novo CRR',
                          ),
                        ),
                        SizedBox(
                          width: 180,
                          child: _MetricCard(
                            icon: Icons.phonelink_lock_outlined,
                            label: 'Dispositivo',
                            value: _deviceActive ? 'Ativo' : 'Pendente',
                            hint: _deviceName.isEmpty ? 'Sem nome' : _deviceName,
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
                                  'As tarefas mais frequentes ficam acessiveis sem poluir o topo da tela.',
                            ),
                            const SizedBox(height: 16),
                            Wrap(
                              spacing: 12,
                              runSpacing: 12,
                              children: [
                                SizedBox(
                                  width: 180,
                                  child: _ActionCard(
                                    icon: Icons.search_rounded,
                                    title: 'Consultar CRRs',
                                    subtitle: 'Busque, revise e acompanhe registros.',
                                    onTap: _busy ? null : _openSearch,
                                  ),
                                ),
                                SizedBox(
                                  width: 180,
                                  child: _ActionCard(
                                    icon: Icons.sync_rounded,
                                    title: 'Sincronizar',
                                    subtitle: _syncing
                                        ? 'Enviando rascunhos pendentes...'
                                        : 'Enviar ${_drafts.length} item(ns) quando houver rede.',
                                    onTap: _busy || _syncing ? null : _syncDrafts,
                                  ),
                                ),
                                SizedBox(
                                  width: 180,
                                  child: _ActionCard(
                                    icon: Icons.refresh_rounded,
                                    title: 'Atualizar painel',
                                    subtitle: 'Recarregue status do dispositivo e historico.',
                                    onTap: _busy ? null : _loadDashboard,
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
                            _SectionHeader(
                              title: 'Status operacional e dispositivo',
                              subtitle: _drafts.isEmpty
                                  ? 'Acompanhe aqui o status atual e a identificacao deste dispositivo.'
                                  : 'Ha rascunhos locais aguardando sincronizacao e a identificacao deste dispositivo.',
                            ),
                            const SizedBox(height: 16),
                            _StatusLine(
                              icon: Icons.sync_problem_outlined,
                              label: 'Sincronizacao',
                              value: _drafts.isEmpty
                                  ? 'Nenhum rascunho pendente'
                                  : '${_drafts.length} rascunho(s) pendente(s)',
                            ),
                            const SizedBox(height: 12),
                            _StatusLine(
                              icon: Icons.smartphone_rounded,
                              label: 'Dispositivo',
                              value: _deviceName.isEmpty ? 'Sem status disponivel' : _deviceName,
                            ),
                            if (_deviceId.isNotEmpty) ...[
                              const SizedBox(height: 12),
                              _StatusLine(
                                icon: Icons.fingerprint_rounded,
                                label: 'Identificador do dispositivo',
                                value: _deviceId,
                              ),
                            ],
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
    final enabled = onTap != null;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(22),
      child: Ink(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: enabled
              ? colorScheme.surfaceContainerHighest
              : colorScheme.surfaceContainerLowest,
          borderRadius: BorderRadius.circular(22),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 42,
              height: 42,
              decoration: BoxDecoration(
                color: enabled
                    ? colorScheme.primaryContainer
                    : colorScheme.surfaceContainer,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(
                icon,
                color: enabled
                    ? colorScheme.onPrimaryContainer
                    : colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 14),
            Text(
              title,
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w700,
                    color: enabled
                        ? colorScheme.onSurface
                        : colorScheme.onSurfaceVariant,
                  ),
            ),
            const SizedBox(height: 6),
            Text(
              subtitle,
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

class _StatusLine extends StatelessWidget {
  const _StatusLine({
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
          child: Icon(icon, color: colorScheme.primary),
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
