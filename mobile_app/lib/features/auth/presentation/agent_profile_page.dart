import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../models/agent_profile.dart';
import '../services/auth_service.dart';

class AgentProfilePage extends StatefulWidget {
  const AgentProfilePage({
    required this.authService,
    super.key,
  });

  final AuthService authService;

  @override
  State<AgentProfilePage> createState() => _AgentProfilePageState();
}

class _AgentProfilePageState extends State<AgentProfilePage> {
  final _profileFormKey = GlobalKey<FormState>();
  final _passwordFormKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _deviceNameController = TextEditingController();
  final _currentPasswordController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  bool _loading = true;
  bool _savingProfile = false;
  bool _changingPassword = false;
  bool _obscureCurrentPassword = true;
  bool _obscureNewPassword = true;
  bool _obscureConfirmPassword = true;

  AgentProfile? _profile;
  String _matricula = '';

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _deviceNameController.dispose();
    _currentPasswordController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _loadProfile() async {
    setState(() => _loading = true);

    final storedMatricula = await widget.authService.readMatricula();
    final storedName = await widget.authService.readAgentName();

    try {
      final profile = await widget.authService.fetchProfile();
      if (!mounted) {
        return;
      }
      _applyProfile(profile);
    } catch (error) {
      if (!mounted) {
        return;
      }
      _matricula = storedMatricula ?? '';
      _nameController.text = storedName ?? '';
      _showMessage(error.toString(), isError: true);
    } finally {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  void _applyProfile(AgentProfile profile) {
    _profile = profile;
    _matricula = profile.matricula.isNotEmpty
        ? profile.matricula
        : _matricula;
    _nameController.text = profile.agentName;
    _deviceNameController.text = profile.deviceName;
  }

  String get _initials {
    final source = _nameController.text.trim().isNotEmpty
        ? _nameController.text.trim()
        : _matricula;
    if (source.isEmpty) {
      return 'AG';
    }
    final parts = source.split(RegExp(r'\s+'));
    if (parts.length >= 2) {
      return '${parts.first[0]}${parts[1][0]}'.toUpperCase();
    }
    return source.substring(0, source.length >= 2 ? 2 : 1).toUpperCase();
  }

  bool get _deviceAuthorized {
    final profile = _profile;
    if (profile == null) {
      return false;
    }
    return profile.deviceActive && profile.deviceActivated;
  }

  Future<void> _saveProfile() async {
    if (!_profileFormKey.currentState!.validate()) {
      return;
    }

    final originalName = _profile?.agentName ?? '';
    final originalDevice = _profile?.deviceName ?? '';
    final newName = _nameController.text.trim();
    final newDevice = _deviceNameController.text.trim();

    if (newName == originalName && newDevice == originalDevice) {
      _showMessage('Nenhuma alteracao para salvar.');
      return;
    }

    setState(() => _savingProfile = true);
    try {
      final profile = await widget.authService.updateProfile(
        agentName: newName != originalName ? newName : null,
        deviceName: newDevice != originalDevice ? newDevice : null,
      );
      if (!mounted) {
        return;
      }
      _applyProfile(profile);
      _showMessage('Perfil atualizado com sucesso.');
      Navigator.of(context).pop(true);
    } catch (error) {
      _showMessage(error.toString(), isError: true);
    } finally {
      if (mounted) {
        setState(() => _savingProfile = false);
      }
    }
  }

  Future<void> _changePassword() async {
    if (!_passwordFormKey.currentState!.validate()) {
      return;
    }

    setState(() => _changingPassword = true);
    try {
      await widget.authService.changePassword(
        currentPassword: _currentPasswordController.text,
        newPassword: _newPasswordController.text,
      );
      if (!mounted) {
        return;
      }
      _currentPasswordController.clear();
      _newPasswordController.clear();
      _confirmPasswordController.clear();
      _showMessage('Senha alterada com sucesso.');
    } catch (error) {
      _showMessage(error.toString(), isError: true);
    } finally {
      if (mounted) {
        setState(() => _changingPassword = false);
      }
    }
  }

  void _showMessage(String message, {bool isError = false}) {
    if (!mounted) {
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message.replaceFirst('Exception: ', '')),
        backgroundColor: isError ? Theme.of(context).colorScheme.error : null,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Meu perfil'),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadProfile,
              child: ListView(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
                children: [
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        children: [
                          CircleAvatar(
                            radius: 40,
                            backgroundColor: colorScheme.primaryContainer,
                            foregroundColor: colorScheme.onPrimaryContainer,
                            child: Text(
                              _initials,
                              style: const TextStyle(
                                fontSize: 28,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                          ),
                          const SizedBox(height: 14),
                          Text(
                            _nameController.text.trim().isNotEmpty
                                ? _nameController.text.trim()
                                : 'Agente',
                            textAlign: TextAlign.center,
                            style: Theme.of(context)
                                .textTheme
                                .titleLarge
                                ?.copyWith(fontWeight: FontWeight.w800),
                          ),
                          if (_matricula.isNotEmpty) ...[
                            const SizedBox(height: 6),
                            Text(
                              'Matricula $_matricula',
                              style: Theme.of(context)
                                  .textTheme
                                  .bodyMedium
                                  ?.copyWith(
                                    color: colorScheme.onSurfaceVariant,
                                  ),
                            ),
                          ],
                          const SizedBox(height: 12),
                          _DeviceStatusBadge(authorized: _deviceAuthorized),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Identificacao',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.w800,
                          color: colorScheme.primary,
                        ),
                  ),
                  const SizedBox(height: 8),
                  Form(
                    key: _profileFormKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Card(
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: TextFormField(
                              controller: _nameController,
                              textCapitalization: TextCapitalization.words,
                              textInputAction: TextInputAction.next,
                              enabled: !_savingProfile,
                              decoration: const InputDecoration(
                                labelText: 'Nome',
                                hintText: 'Seu nome completo',
                                prefixIcon: Icon(Icons.person_outline_rounded),
                              ),
                              validator: (value) {
                                if ((value ?? '').trim().length < 2) {
                                  return 'Informe um nome valido.';
                                }
                                return null;
                              },
                            ),
                          ),
                        ),
                        const SizedBox(height: 20),
                        Text(
                          'Dispositivo',
                          style:
                              Theme.of(context).textTheme.titleSmall?.copyWith(
                                    fontWeight: FontWeight.w800,
                                    color: colorScheme.primary,
                                  ),
                        ),
                        const SizedBox(height: 8),
                        Card(
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                TextFormField(
                                  controller: _deviceNameController,
                                  textInputAction: TextInputAction.done,
                                  enabled: !_savingProfile,
                                  decoration: const InputDecoration(
                                    labelText: 'Nome do dispositivo',
                                    hintText: 'Ex.: Celular da equipe 01',
                                    prefixIcon:
                                        Icon(Icons.smartphone_outlined),
                                  ),
                                  validator: (value) {
                                    if ((value ?? '').trim().length < 2) {
                                      return 'Informe um nome para o dispositivo.';
                                    }
                                    return null;
                                  },
                                ),
                                if ((_profile?.deviceId ?? '').isNotEmpty) ...[
                                  const SizedBox(height: 12),
                                  InputDecorator(
                                    decoration: const InputDecoration(
                                      labelText: 'Identificador',
                                      prefixIcon:
                                          Icon(Icons.fingerprint_outlined),
                                    ),
                                    child: Row(
                                      children: [
                                        Expanded(
                                          child: Text(
                                            _profile!.deviceId,
                                            style: Theme.of(context)
                                                .textTheme
                                                .bodyMedium
                                                ?.copyWith(
                                                  fontWeight: FontWeight.w600,
                                                ),
                                          ),
                                        ),
                                        IconButton(
                                          onPressed: () {
                                            Clipboard.setData(
                                              ClipboardData(
                                                text: _profile!.deviceId,
                                              ),
                                            );
                                            _showMessage(
                                              'Identificador copiado.',
                                            );
                                          },
                                          icon: const Icon(Icons.copy_rounded),
                                          tooltip: 'Copiar identificador',
                                        ),
                                      ],
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
                  const SizedBox(height: 20),
                  Text(
                    'Seguranca',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.w800,
                          color: colorScheme.primary,
                        ),
                  ),
                  const SizedBox(height: 8),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Form(
                        key: _passwordFormKey,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            if (_profile != null && !_profile!.passwordChanged)
                              Padding(
                                padding: const EdgeInsets.only(bottom: 12),
                                child: Material(
                                  color: colorScheme.tertiaryContainer
                                      .withOpacity(0.45),
                                  borderRadius: BorderRadius.circular(12),
                                  child: Padding(
                                    padding: const EdgeInsets.all(12),
                                    child: Row(
                                      children: [
                                        Icon(
                                          Icons.info_outline_rounded,
                                          color: colorScheme.tertiary,
                                          size: 20,
                                        ),
                                        const SizedBox(width: 10),
                                        Expanded(
                                          child: Text(
                                            'Recomendamos alterar a senha padrao no primeiro acesso.',
                                            style: Theme.of(context)
                                                .textTheme
                                                .bodySmall,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              ),
                            TextFormField(
                              controller: _currentPasswordController,
                              obscureText: _obscureCurrentPassword,
                              enabled: !_changingPassword,
                              decoration: InputDecoration(
                                labelText: 'Senha atual',
                                prefixIcon:
                                    const Icon(Icons.lock_outline_rounded),
                                suffixIcon: IconButton(
                                  onPressed: () => setState(
                                    () => _obscureCurrentPassword =
                                        !_obscureCurrentPassword,
                                  ),
                                  icon: Icon(
                                    _obscureCurrentPassword
                                        ? Icons.visibility_outlined
                                        : Icons.visibility_off_outlined,
                                  ),
                                ),
                              ),
                              validator: (value) {
                                if ((value ?? '').isEmpty) {
                                  return 'Informe a senha atual.';
                                }
                                return null;
                              },
                            ),
                            const SizedBox(height: 12),
                            TextFormField(
                              controller: _newPasswordController,
                              obscureText: _obscureNewPassword,
                              enabled: !_changingPassword,
                              decoration: InputDecoration(
                                labelText: 'Nova senha',
                                prefixIcon:
                                    const Icon(Icons.lock_reset_rounded),
                                suffixIcon: IconButton(
                                  onPressed: () => setState(
                                    () => _obscureNewPassword =
                                        !_obscureNewPassword,
                                  ),
                                  icon: Icon(
                                    _obscureNewPassword
                                        ? Icons.visibility_outlined
                                        : Icons.visibility_off_outlined,
                                  ),
                                ),
                              ),
                              validator: (value) {
                                if ((value ?? '').length < 4) {
                                  return 'A nova senha deve ter ao menos 4 caracteres.';
                                }
                                if (value == 'admin') {
                                  return 'Escolha uma senha diferente de "admin".';
                                }
                                return null;
                              },
                            ),
                            const SizedBox(height: 12),
                            TextFormField(
                              controller: _confirmPasswordController,
                              obscureText: _obscureConfirmPassword,
                              enabled: !_changingPassword,
                              textInputAction: TextInputAction.done,
                              decoration: InputDecoration(
                                labelText: 'Confirmar nova senha',
                                prefixIcon:
                                    const Icon(Icons.lock_outline_rounded),
                                suffixIcon: IconButton(
                                  onPressed: () => setState(
                                    () => _obscureConfirmPassword =
                                        !_obscureConfirmPassword,
                                  ),
                                  icon: Icon(
                                    _obscureConfirmPassword
                                        ? Icons.visibility_outlined
                                        : Icons.visibility_off_outlined,
                                  ),
                                ),
                              ),
                              validator: (value) {
                                if (value != _newPasswordController.text) {
                                  return 'As senhas nao coincidem.';
                                }
                                return null;
                              },
                            ),
                            const SizedBox(height: 16),
                            OutlinedButton(
                              onPressed: _changingPassword ? null : _changePassword,
                              child: _changingPassword
                                  ? const SizedBox(
                                      width: 22,
                                      height: 22,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                      ),
                                    )
                                  : const Text('Alterar senha'),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  FilledButton(
                    onPressed: _savingProfile ? null : _saveProfile,
                    child: _savingProfile
                        ? const SizedBox(
                            width: 22,
                            height: 22,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : const Text('Salvar alteracoes'),
                  ),
                ],
              ),
            ),
    );
  }
}

class _DeviceStatusBadge extends StatelessWidget {
  const _DeviceStatusBadge({required this.authorized});

  final bool authorized;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final color = authorized ? const Color(0xFF2E7D32) : colorScheme.tertiary;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: authorized
            ? const Color(0xFFE8F5E9)
            : colorScheme.tertiaryContainer.withOpacity(0.5),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            authorized
                ? Icons.verified_user_outlined
                : Icons.phonelink_lock_outlined,
            size: 16,
            color: color,
          ),
          const SizedBox(width: 6),
          Text(
            authorized ? 'Dispositivo autorizado' : 'Aguardando liberacao',
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w700,
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }
}
