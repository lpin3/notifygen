import 'package:flutter/material.dart';

import '../../../core/http/api_client.dart';
import '../../../core/storage/app_storage.dart';
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
  late final AuthService _authService;
  late final CrrService _crrService;
  final _deviceNameController = TextEditingController(text: 'Dispositivo Flutter');
  final _codeController = TextEditingController();
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
    _deviceNameController.dispose();
    _codeController.dispose();
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

  Future<void> _registerDevice() async {
    setState(() => _busy = true);
    try {
      final result = await _authService.registerDevice(
        deviceName: _deviceNameController.text.trim().isEmpty
            ? 'Dispositivo Flutter'
            : _deviceNameController.text.trim(),
        deviceId: _deviceId,
      );

      if (!mounted) {
        return;
      }

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(result.message)),
      );
    } catch (error) {
      _showError(error.toString());
    } finally {
      if (mounted) {
        setState(() => _busy = false);
      }
    }
  }

  Future<void> _activateDevice() async {
    setState(() => _busy = true);
    try {
      final activation = await _authService.activateDevice(
        code: _codeController.text.trim(),
        matricula: _matriculaController.text.trim(),
        senha: _senhaController.text.trim(),
      );

      final apiKey = await _authService.readApiKey();
      if (apiKey != null && apiKey.isNotEmpty) {
        await _authService.validateLogin(
          apiKey: apiKey,
          matricula: _matriculaController.text.trim(),
          senha: _senhaController.text.trim(),
        );
      }

      if (!mounted) {
        return;
      }

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            activation.senhaAlterada
                ? 'Dispositivo ativado com sucesso.'
                : 'Ativado. O agente ainda usa a senha inicial.',
          ),
        ),
      );
      _openHome();
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
    return Scaffold(
      appBar: AppBar(title: const Text('Notifygen Mobile')),
      body: _busy
          ? const Center(child: CircularProgressIndicator())
          : SafeArea(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Identificador do dispositivo',
                              style: TextStyle(fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(height: 8),
                            SelectableText(_deviceId),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _deviceNameController,
                      decoration: const InputDecoration(
                        labelText: 'Nome do dispositivo',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    FilledButton(
                      onPressed: _registerDevice,
                      child: const Text('Registrar dispositivo'),
                    ),
                    const SizedBox(height: 24),
                    TextField(
                      controller: _codeController,
                      decoration: const InputDecoration(
                        labelText: 'Codigo de ativacao',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _matriculaController,
                      decoration: const InputDecoration(
                        labelText: 'Matricula do agente',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _senhaController,
                      obscureText: true,
                      decoration: const InputDecoration(
                        labelText: 'Senha',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    FilledButton(
                      onPressed: _activateDevice,
                      child: const Text('Ativar e entrar'),
                    ),
                  ],
                ),
              ),
            ),
    );
  }
}
