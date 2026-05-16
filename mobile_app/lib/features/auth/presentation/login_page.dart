import 'package:flutter/material.dart';

import '../../../core/http/api_client.dart';
import '../../../core/storage/app_storage.dart';
import '../../../core/widgets/app_logo.dart';
import '../models/access_request_result.dart';
import 'access_status_page.dart';
import '../../crr/services/crr_service.dart';
import '../../home/presentation/home_page.dart';
import '../services/auth_service.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({
    required this.storage,
    required this.apiClient,
    this.initialDeviceId,
    this.initialMatricula,
    super.key,
  });

  final AppStorage storage;
  final ApiClient apiClient;
  final String? initialDeviceId;
  final String? initialMatricula;

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  static const String _defaultDeviceName = 'Dispositivo operacional';

  late final AuthService _authService;
  late final CrrService _crrService;
  final _formKey = GlobalKey<FormState>();
  final _matriculaController = TextEditingController();
  final _senhaController = TextEditingController();

  String _deviceId = '';
  bool _busy = true;
  bool _submitting = false;
  bool _obscurePassword = true;

  @override
  void initState() {
    super.initState();
    _authService = AuthService(apiClient: widget.apiClient, storage: widget.storage);
    _crrService = CrrService(apiClient: widget.apiClient);

    final initialMatricula = widget.initialMatricula?.trim() ?? '';
    if (initialMatricula.isNotEmpty) {
      _matriculaController.text = initialMatricula;
    }

    if ((widget.initialDeviceId ?? '').isNotEmpty) {
      _deviceId = widget.initialDeviceId!;
      _busy = false;
    } else {
      _bootstrap();
    }
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
    if (!(_formKey.currentState?.validate() ?? false)) {
      return;
    }

    FocusScope.of(context).unfocus();
    setState(() => _submitting = true);
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
        setState(() => _submitting = false);
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
      body: _busy
          ? const Center(child: CircularProgressIndicator())
          : GestureDetector(
              onTap: () => FocusScope.of(context).unfocus(),
              child: SafeArea(
                child: Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 480),
                    child: SingleChildScrollView(
                      padding: const EdgeInsets.fromLTRB(20, 24, 20, 32),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Container(
                            padding: const EdgeInsets.all(24),
                            decoration: BoxDecoration(
                              color: colorScheme.primaryContainer.withOpacity(0.52),
                              borderRadius: BorderRadius.circular(28),
                              border: Border.all(color: colorScheme.outlineVariant),
                            ),
                            child: Column(
                              children: [
                                const AppLogo(size: 72),
                                const SizedBox(height: 20),
                                Text(
                                  'Acesso operacional',
                                  textAlign: TextAlign.center,
                                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                        fontWeight: FontWeight.w800,
                                      ),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  'Entre com sua matrícula e senha para acessar o painel. A identificação do dispositivo fica disponível após o login.',
                                  textAlign: TextAlign.center,
                                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                        color: colorScheme.onSurfaceVariant,
                                      ),
                                ),
                                const SizedBox(height: 16),
                                Wrap(
                                  alignment: WrapAlignment.center,
                                  spacing: 8,
                                  runSpacing: 8,
                                  children: [
                                    _HeaderPill(
                                      icon: Icons.verified_user_outlined,
                                      label: 'Acesso seguro',
                                      foregroundColor: colorScheme.primary,
                                      backgroundColor: colorScheme.surface.withOpacity(0.88),
                                    ),
                                    _HeaderPill(
                                      icon: Icons.bolt_rounded,
                                      label: 'Entrada rapida',
                                      foregroundColor: colorScheme.primary,
                                      backgroundColor: colorScheme.surface.withOpacity(0.88),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 20),
                          Card(
                            child: Padding(
                              padding: const EdgeInsets.all(20),
                              child: Form(
                                key: _formKey,
                                child: AutofillGroup(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.stretch,
                                    children: [
                                      Text(
                                        'Entrar no aplicativo',
                                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                              fontWeight: FontWeight.w700,
                                            ),
                                      ),
                                      const SizedBox(height: 6),
                                      Text(
                                        'Use as credenciais do ambiente operacional para continuar.',
                                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                              color: colorScheme.onSurfaceVariant,
                                            ),
                                      ),
                                      const SizedBox(height: 20),
                                      TextFormField(
                                        controller: _matriculaController,
                                        keyboardType: TextInputType.number,
                                        textInputAction: TextInputAction.next,
                                        autofillHints: const [AutofillHints.username],
                                        enabled: !_submitting,
                                        decoration: const InputDecoration(
                                          labelText: 'Matrícula',
                                          hintText: 'Digite sua matrícula',
                                          prefixIcon: Icon(Icons.badge_outlined),
                                        ),
                                        validator: (value) {
                                          if ((value ?? '').trim().isEmpty) {
                                            return 'Informe sua matrícula.';
                                          }
                                          return null;
                                        },
                                      ),
                                      const SizedBox(height: 12),
                                      TextFormField(
                                        controller: _senhaController,
                                        obscureText: _obscurePassword,
                                        textInputAction: TextInputAction.done,
                                        autofillHints: const [AutofillHints.password],
                                        enabled: !_submitting,
                                        onFieldSubmitted: (_) {
                                          if (!_submitting) {
                                            _submitAccess();
                                          }
                                        },
                                        decoration: InputDecoration(
                                          labelText: 'Senha',
                                          hintText: 'Digite sua senha',
                                          prefixIcon: const Icon(Icons.lock_outline_rounded),
                                          suffixIcon: IconButton(
                                            onPressed: () {
                                              setState(
                                                () => _obscurePassword = !_obscurePassword,
                                              );
                                            },
                                            icon: Icon(
                                              _obscurePassword
                                                  ? Icons.visibility_outlined
                                                  : Icons.visibility_off_outlined,
                                            ),
                                            tooltip: _obscurePassword
                                                ? 'Mostrar senha'
                                                : 'Ocultar senha',
                                          ),
                                        ),
                                        validator: (value) {
                                          if ((value ?? '').trim().isEmpty) {
                                            return 'Informe sua senha.';
                                          }
                                          return null;
                                        },
                                      ),
                                      const SizedBox(height: 20),
                                      FilledButton(
                                        onPressed: _submitting ? null : _submitAccess,
                                        child: _submitting
                                            ? SizedBox(
                                                height: 22,
                                                width: 22,
                                                child: CircularProgressIndicator(
                                                  strokeWidth: 2.4,
                                                  valueColor: AlwaysStoppedAnimation<Color>(
                                                    colorScheme.onPrimary,
                                                  ),
                                                ),
                                              )
                                            : const Text('Entrar no aplicativo'),
                                      ),
                                      const SizedBox(height: 14),
                                      Container(
                                        padding: const EdgeInsets.all(14),
                                        decoration: BoxDecoration(
                                          color: colorScheme.surfaceContainerHighest,
                                          borderRadius: BorderRadius.circular(16),
                                        ),
                                        child: Row(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Icon(
                                              Icons.info_outline_rounded,
                                              size: 20,
                                              color: colorScheme.primary,
                                            ),
                                            const SizedBox(width: 10),
                                            Expanded(
                                              child: Text(
                                                'O app reconhece o dispositivo automaticamente. O identificador e o status de liberação ficam disponíveis no painel após o acesso.',
                                                style: Theme.of(context)
                                                    .textTheme
                                                    .bodySmall
                                                    ?.copyWith(
                                                      color: colorScheme.onSurfaceVariant,
                                                    ),
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
    );
  }
}

class _HeaderPill extends StatelessWidget {
  const _HeaderPill({
    required this.icon,
    required this.label,
    required this.foregroundColor,
    required this.backgroundColor,
  });

  final IconData icon;
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
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: foregroundColor),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(
              color: foregroundColor,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}

