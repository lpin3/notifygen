import 'package:flutter/material.dart';

import '../../../core/http/api_client.dart';
import '../../../core/storage/app_storage.dart';
import '../models/access_request_result.dart';
import 'access_status_page.dart';
import '../../crr/services/crr_service.dart';
import '../../home/presentation/home_page.dart';
import '../services/auth_service.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({
    required this.storage,
    required this.apiClient,
    super.key,
  });

  final AppStorage storage;
  final ApiClient apiClient;

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  static const String _defaultDeviceName = 'Dispositivo operacional';

  late final AuthService _authService;
  late final CrrService _crrService;
  final _matriculaController = TextEditingController();
  final _senhaController = TextEditingController();

  String _deviceId = '';
  bool _busy = true;

  @override
  void initState() {
    super.initState();
    _authService = AuthService(apiClient: widget.apiClient, storage: widget.storage);
    _crrService = CrrService(apiClient: widget.apiClient);
    _bootstrap();
  }

  @override
  void dispose() {
    _matriculaController.dispose();
    _senhaController.dispose();
    super.dispose();
  }

  Future<void> _bootstrap() async {
    final deviceId = await _authService.getOrCreateDeviceId();
    final hasSession = await _authService.hasSession();
    final matricula = await _authService.readMatricula();

    if (!mounted) {
      return;
    }

    setState(() {
      _deviceId = deviceId;
      if ((matricula ?? '').isNotEmpty) {
        _matriculaController.text = matricula!;
      }
      _busy = false;
    });

    if (hasSession) {
      _openHome();
    }
  }

  Future<AccessRequestResult> _requestAccess() {
    final matricula = _matriculaController.text.trim();
    final senha = _senhaController.text.trim();

    if (matricula.isEmpty || senha.isEmpty) {
      throw Exception('Informe matrícula e senha para continuar.');
    }

    return _authService.requestAccess(
      deviceId: _deviceId,
      deviceName: _defaultDeviceName,
      matricula: matricula,
      senha: senha,
    );
  }

  Future<void> _submitAccess() async {
    setState(() => _busy = true);
    try {
      final result = await _requestAccess();

      if (!mounted) {
        return;
      }

      if (result.isApproved) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Acesso liberado com sucesso.')),
        );
        _openHome();
        return;
      }

      final updatedResult = await Navigator.of(context).push<AccessRequestResult>(
        MaterialPageRoute<AccessRequestResult>(
          builder: (_) => AccessStatusPage(
            initialResult: result,
            onRefreshStatus: _requestAccess,
          ),
        ),
      );

      if (!mounted) {
        return;
      }

      if (updatedResult?.isApproved ?? false) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Dispositivo aprovado. Entrando no app...')),
        );
        _openHome();
      }
    } catch (error) {
      _showError(error.toString());
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }

  void _openHome() {
    Navigator.of(context).pushReplacement(
      MaterialPageRoute<void>(
        builder: (_) => HomePage(
          authService: _authService,
          crrService: _crrService,
        ),
      ),
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

    return Scaffold(
      appBar: AppBar(title: const Text('Notifygen Operacional')),
      body: _busy
          ? const Center(child: CircularProgressIndicator())
          : SafeArea(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
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
                            'Acesso operacional',
                            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                  color: colorScheme.onPrimary,
                                  fontWeight: FontWeight.w700,
                                ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Digite sua matrícula e senha. O app identifica o dispositivo automaticamente e informa se ele já está liberado, pendente ou bloqueado.',
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                  color: colorScheme.onPrimary,
                                ),
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
                              'Identificação do dispositivo',
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                    fontWeight: FontWeight.w700,
                                  ),
                            ),
                            const SizedBox(height: 12),
                            Container(
                              padding: const EdgeInsets.all(14),
                              decoration: BoxDecoration(
                                color: colorScheme.surfaceContainerHighest,
                                borderRadius: BorderRadius.circular(18),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text(
                                    'Identificador do dispositivo',
                                    style: TextStyle(fontWeight: FontWeight.w700),
                                  ),
                                  const SizedBox(height: 8),
                                  SelectableText(_deviceId),
                                ],
                              ),
                            ),
                            const SizedBox(height: 12),
                            Text(
                              'Este identificador é enviado junto com a autenticação do agente para registrar ou localizar o aparelho no backend.',
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(18),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Text(
                              'Entrar no aplicativo',
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                    fontWeight: FontWeight.w700,
                                  ),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _matriculaController,
                              keyboardType: TextInputType.number,
                              decoration: const InputDecoration(
                                labelText: 'Matrícula do agente',
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _senhaController,
                              obscureText: true,
                              decoration: const InputDecoration(
                                labelText: 'Senha',
                              ),
                            ),
                            const SizedBox(height: 16),
                            FilledButton(
                              onPressed: _busy ? null : _submitAccess,
                              child: const Text('Entrar no aplicativo'),
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
                              'Fluxo recomendado',
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                    fontWeight: FontWeight.w700,
                                  ),
                            ),
                            const SizedBox(height: 12),
                            const _FlowItem(
                              index: '1',
                              title: 'Autenticação do agente',
                              description:
                                  'O app valida matrícula e senha antes de qualquer tentativa de operação.',
                            ),
                            const SizedBox(height: 12),
                            const _FlowItem(
                              index: '2',
                              title: 'Identificação automática do aparelho',
                              description:
                                  'O backend localiza ou registra o dispositivo pelo identificador interno, sem o usuário decidir se é primeiro acesso.',
                            ),
                            const SizedBox(height: 12),
                            const _FlowItem(
                              index: '3',
                              title: 'Liberação administrativa segura',
                              description:
                                  'Se o aparelho ainda não estiver aprovado, o agente vê o status da solicitação e pode acompanhar a liberação sem códigos manuais.',
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
    );
  }
}

class _FlowItem extends StatelessWidget {
  const _FlowItem({
    required this.index,
    required this.title,
    required this.description,
  });

  final String index;
  final String title;
  final String description;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        CircleAvatar(
          radius: 14,
          backgroundColor: colorScheme.primaryContainer,
          child: Text(
            index,
            style: TextStyle(
              color: colorScheme.onPrimaryContainer,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),
        const SizedBox(width: 12),
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
              const SizedBox(height: 4),
              Text(description),
            ],
          ),
        ),
      ],
    );
  }
}
