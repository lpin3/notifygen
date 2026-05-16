import 'dart:async';

import 'package:flutter/material.dart';

import '../../../core/http/api_client.dart';
import '../../../core/storage/app_storage.dart';
import '../../../core/widgets/app_logo.dart';
import '../../auth/presentation/login_page.dart';
import '../../auth/services/auth_service.dart';
import '../../crr/services/crr_service.dart';
import '../../home/presentation/home_page.dart';

class SplashPage extends StatefulWidget {
  const SplashPage({
    required this.storage,
    required this.apiClient,
    super.key,
  });

  final AppStorage storage;
  final ApiClient apiClient;

  @override
  State<SplashPage> createState() => _SplashPageState();
}

class _SplashPageState extends State<SplashPage> {
  @override
  void initState() {
    super.initState();
    _bootstrap();
  }

  Future<void> _bootstrap() async {
    final authService = AuthService(
      apiClient: widget.apiClient,
      storage: widget.storage,
    );
    final crrService = CrrService(apiClient: widget.apiClient);

    try {
      final results = await Future.wait<Object?>([
        Future<void>.delayed(const Duration(milliseconds: 1400)),
        authService.getOrCreateDeviceId(),
        authService.readMatricula(),
        authService.hasSession(),
      ]);

      if (!mounted) {
        return;
      }

      final deviceId = results[1] as String;
      final matricula = results[2] as String?;
      final hasSession = results[3] as bool;

      if (hasSession) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute<void>(
            builder: (_) => HomePage(
              authService: authService,
              crrService: crrService,
            ),
          ),
        );
        return;
      }

      Navigator.of(context).pushReplacement(
        MaterialPageRoute<void>(
          builder: (_) => LoginPage(
            storage: widget.storage,
            apiClient: widget.apiClient,
            initialDeviceId: deviceId,
            initialMatricula: matricula,
          ),
        ),
      );
    } catch (_) {
      if (!mounted) {
        return;
      }

      Navigator.of(context).pushReplacement(
        MaterialPageRoute<void>(
          builder: (_) => LoginPage(
            storage: widget.storage,
            apiClient: widget.apiClient,
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      body: DecoratedBox(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              colorScheme.surface,
              colorScheme.primaryContainer.withOpacity(0.55),
            ],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const AppLogo(size: 104),
                const SizedBox(height: 28),
                SizedBox(
                  width: 34,
                  height: 34,
                  child: CircularProgressIndicator(
                    strokeWidth: 3,
                    color: colorScheme.primary,
                  ),
                ),
                const SizedBox(height: 18),
                Text(
                  'Preparando ambiente operacional',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const SizedBox(height: 6),
                Text(
                  'Conectando dispositivo e carregando sua sessão.',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: colorScheme.onSurfaceVariant,
                      ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
