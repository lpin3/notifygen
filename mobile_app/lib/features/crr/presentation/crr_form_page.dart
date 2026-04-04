import 'package:flutter/material.dart';

import '../../auth/services/auth_service.dart';
import '../models/crr_create_payload.dart';
import '../models/crr_draft.dart';
import '../models/enquadramento_item.dart';
import '../services/crr_draft_service.dart';
import '../services/crr_service.dart';

class CrrFormPage extends StatefulWidget {
  const CrrFormPage({
    required this.authService,
    required this.crrService,
    required this.draftService,
    this.existingDraft,
    super.key,
  });

  final AuthService authService;
  final CrrService crrService;
  final CrrDraftService draftService;
  final CrrDraft? existingDraft;

  @override
  State<CrrFormPage> createState() => _CrrFormPageState();
}

class _CrrFormPageState extends State<CrrFormPage> {
  final _numeroController = TextEditingController();
  final _localController = TextEditingController();
  final _municipioController =
      TextEditingController(text: 'São Sebastião - SP');
  final _dataController = TextEditingController();
  final _horaController = TextEditingController();
  final _medidaController =
      TextEditingController(text: 'Remoção do veículo ao Depósito');
  final _patioController = TextEditingController();
  final _placaGuinchoController = TextEditingController();
  final _encarregadoController = TextEditingController();
  final _observacaoController = TextEditingController();
  final _placaController = TextEditingController();
  final _chassiController = TextEditingController();
  final _marcaController = TextEditingController();
  final _modeloController = TextEditingController();
  final _corController = TextEditingController();
  final _nomeCondutorController = TextEditingController();
  final _cpfController = TextEditingController();
  final _cnhController = TextEditingController();
  final _cnhEstrangeiraController = TextEditingController();
  final _aitController = TextEditingController();
  final _enquadramentoManualController = TextEditingController();

  int _currentStep = 0;
  bool _busy = true;
  bool _submitting = false;
  bool _vehicleUnknown = false;
  String _matricula = '';
  String _draftId = '';
  List<String> _aits = <String>[];
  List<String> _selectedEnquadramentos = <String>[];
  List<EnquadramentoItem> _enquadramentos = <EnquadramentoItem>[];

  @override
  void initState() {
    super.initState();
    _bootstrap();
  }

  @override
  void dispose() {
    _numeroController.dispose();
    _localController.dispose();
    _municipioController.dispose();
    _dataController.dispose();
    _horaController.dispose();
    _medidaController.dispose();
    _patioController.dispose();
    _placaGuinchoController.dispose();
    _encarregadoController.dispose();
    _observacaoController.dispose();
    _placaController.dispose();
    _chassiController.dispose();
    _marcaController.dispose();
    _modeloController.dispose();
    _corController.dispose();
    _nomeCondutorController.dispose();
    _cpfController.dispose();
    _cnhController.dispose();
    _cnhEstrangeiraController.dispose();
    _aitController.dispose();
    _enquadramentoManualController.dispose();
    super.dispose();
  }

  Future<void> _bootstrap() async {
    final matricula = await widget.authService.readMatricula() ?? '';
    final payload = widget.existingDraft?.payload;
    final now = DateTime.now();

    _matricula = payload?.matriculaAgente.isNotEmpty == true
        ? payload!.matriculaAgente
        : matricula;
    _draftId = widget.existingDraft?.id ?? '';
    _numeroController.text = payload?.numeroCrr ?? '';
    _localController.text = payload?.localFiscalizacao ?? '';
    _municipioController.text = payload?.municipioEstadoFiscalizacao.isNotEmpty ==
            true
        ? payload!.municipioEstadoFiscalizacao
        : 'São Sebastião - SP';
    _dataController.text =
        payload?.dataFiscalizacao.isNotEmpty == true
            ? payload!.dataFiscalizacao
            : _formatDate(now);
    _horaController.text =
        payload?.horaFiscalizacao.isNotEmpty == true
            ? payload!.horaFiscalizacao
            : _formatTime(now);
    _medidaController.text = payload?.medidaAdministrativa.isNotEmpty == true
        ? payload!.medidaAdministrativa
        : 'Remoção do veículo ao Depósito';
    _patioController.text = payload?.localPatio ?? '';
    _placaGuinchoController.text = payload?.placaGuincho ?? '';
    _encarregadoController.text = payload?.encarregado ?? '';
    _observacaoController.text = payload?.observacao ?? '';
    _placaController.text = payload?.placa ?? '';
    _chassiController.text = payload?.chassi ?? '';
    _marcaController.text = payload?.marca ?? '';
    _modeloController.text = payload?.modelo ?? '';
    _corController.text = payload?.cor ?? '';
    _nomeCondutorController.text = payload?.nomeCondutor ?? '';
    _cpfController.text = payload?.cpfCondutor ?? '';
    _cnhController.text = payload?.cnh ?? '';
    _cnhEstrangeiraController.text = payload?.cnhEstrangeira ?? '';
    _vehicleUnknown = payload?.veiculoSemIdentificacao ?? false;
    _aits = List<String>.from(payload?.aits ?? const <String>[]);
    _selectedEnquadramentos =
        List<String>.from(payload?.enquadramentos ?? const <String>[]);

    try {
      _enquadramentos = await widget.crrService.listarEnquadramentos();
    } catch (_) {
      _enquadramentos = <EnquadramentoItem>[];
    }

    if (!mounted) {
      return;
    }
    setState(() => _busy = false);
  }

  Future<void> _pickDate() async {
    final initialDate = DateTime.tryParse(_dataController.text) ?? DateTime.now();
    final selected = await showDatePicker(
      context: context,
      initialDate: initialDate,
      firstDate: DateTime(2020),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );
    if (selected == null) {
      return;
    }
    setState(() => _dataController.text = _formatDate(selected));
  }

  Future<void> _pickTime() async {
    final selected = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.now(),
      builder: (context, child) => child ?? const SizedBox.shrink(),
    );
    if (selected == null) {
      return;
    }
    setState(
      () => _horaController.text =
          '${selected.hour.toString().padLeft(2, '0')}:${selected.minute.toString().padLeft(2, '0')}',
    );
  }

  void _addAit() {
    final value = _aitController.text.trim().toUpperCase();
    if (value.isEmpty || _aits.contains(value)) {
      return;
    }
    setState(() {
      _aits = <String>[..._aits, value];
      _aitController.clear();
    });
  }

  void _addEnquadramentoManual() {
    final value = _enquadramentoManualController.text.trim();
    if (value.isEmpty) {
      return;
    }

    final normalized = value.padLeft(5, '0');
    if (_selectedEnquadramentos.contains(normalized)) {
      _enquadramentoManualController.clear();
      return;
    }

    setState(() {
      _selectedEnquadramentos = <String>[
        ..._selectedEnquadramentos,
        normalized,
      ];
      _enquadramentoManualController.clear();
    });
  }

  Future<void> _selectEnquadramentos() async {
    final result = await showModalBottomSheet<List<String>>(
      context: context,
      isScrollControlled: true,
      builder: (context) {
        final searchController = TextEditingController();
        var tempSelected = <String>[..._selectedEnquadramentos];
        var filtered = List<EnquadramentoItem>.from(_enquadramentos);

        return StatefulBuilder(
          builder: (context, setModalState) {
            void applyFilter(String query) {
              final normalized = query.toLowerCase().trim();
              setModalState(() {
                filtered = _enquadramentos.where((item) {
                  return item.codigo.contains(normalized) ||
                      item.descricaoInfracao.toLowerCase().contains(normalized);
                }).toList();
              });
            }

            return SafeArea(
              child: Padding(
                padding: EdgeInsets.only(
                  left: 16,
                  right: 16,
                  top: 16,
                  bottom: MediaQuery.of(context).viewInsets.bottom + 16,
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      'Selecionar enquadramentos',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: searchController,
                      onChanged: applyFilter,
                      decoration: const InputDecoration(
                        labelText: 'Buscar por código ou descrição',
                        prefixIcon: Icon(Icons.search),
                      ),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      height: MediaQuery.of(context).size.height * 0.5,
                      child: ListView(
                        shrinkWrap: true,
                        children: filtered.map((item) {
                          final selected = tempSelected.contains(item.codigo);
                          return CheckboxListTile(
                            value: selected,
                            onChanged: (_) {
                              setModalState(() {
                                if (selected) {
                                  tempSelected.remove(item.codigo);
                                } else {
                                  tempSelected.add(item.codigo);
                                }
                              });
                            },
                            title: Text(item.codigo),
                            subtitle: Text(item.descricaoInfracao),
                            controlAffinity: ListTileControlAffinity.leading,
                          );
                        }).toList(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    FilledButton(
                      onPressed: () => Navigator.of(context).pop(tempSelected),
                      child: const Text('Aplicar seleção'),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );

    if (result == null || !mounted) {
      return;
    }
    setState(() => _selectedEnquadramentos = result);
  }

  Future<void> _saveDraft({String message = 'Rascunho salvo neste dispositivo.'}) async {
    final draft = await widget.draftService.saveDraft(
      draftId: _draftId.isEmpty ? null : _draftId,
      payload: _buildPayload(),
    );

    if (!mounted) {
      return;
    }
    setState(() => _draftId = draft.id);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  Future<void> _submit() async {
    final validationError = _validateBeforeSubmit();
    if (validationError != null) {
      _showMessage(validationError);
      return;
    }

    setState(() => _submitting = true);
    final payload = _buildPayload();

    try {
      await widget.crrService.criarCrr(payload);
      if (_draftId.isNotEmpty) {
        await widget.draftService.removeDraft(_draftId);
      }

      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('CRR enviado com sucesso.'),
        ),
      );
      Navigator.of(context).pop(true);
    } catch (error) {
      final message = error.toString().replaceFirst('Exception: ', '');
      final draft = await widget.draftService.saveDraft(
        draftId: _draftId.isEmpty ? null : _draftId,
        payload: payload,
        lastError: message,
      );

      if (!mounted) {
        return;
      }

      setState(() => _draftId = draft.id);
      await showDialog<void>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Sem envio confirmado'),
          content: Text(
            'Não foi possível enviar o CRR agora.\n\nO conteúdo foi salvo como rascunho local para sincronização posterior.\n\nDetalhe: $message',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Entendi'),
            ),
          ],
        ),
      );
      Navigator.of(context).pop(true);
    } finally {
      if (mounted) {
        setState(() => _submitting = false);
      }
    }
  }

  CrrCreatePayload _buildPayload() {
    return CrrCreatePayload(
      numeroCrr: _numeroController.text.trim().toUpperCase(),
      localFiscalizacao: _localController.text.trim(),
      municipioEstadoFiscalizacao: _municipioController.text.trim(),
      dataFiscalizacao: _dataController.text.trim(),
      horaFiscalizacao: _horaController.text.trim(),
      medidaAdministrativa: _medidaController.text.trim(),
      localPatio: _patioController.text.trim(),
      placaGuincho: _placaGuinchoController.text.trim().toUpperCase(),
      encarregado: _encarregadoController.text.trim(),
      observacao: _observacaoController.text.trim(),
      matriculaAgente: _matricula,
      placa: _vehicleUnknown ? '' : _placaController.text.trim().toUpperCase(),
      chassi: _vehicleUnknown ? '' : _chassiController.text.trim().toUpperCase(),
      marca: _vehicleUnknown ? '' : _marcaController.text.trim(),
      modelo: _vehicleUnknown ? '' : _modeloController.text.trim(),
      cor: _vehicleUnknown ? '' : _corController.text.trim(),
      nomeCondutor: _nomeCondutorController.text.trim(),
      cpfCondutor: _cpfController.text.trim(),
      cnh: _cnhController.text.trim(),
      cnhEstrangeira: _cnhEstrangeiraController.text.trim(),
      aits: _aits,
      enquadramentos: _selectedEnquadramentos,
      veiculoSemIdentificacao: _vehicleUnknown,
    );
  }

  String? _validateBeforeSubmit() {
    if (_matricula.trim().isEmpty) {
      return 'Sessão do agente não encontrada. Entre novamente.';
    }
    if (_localController.text.trim().isEmpty) {
      return 'Informe o local da fiscalização.';
    }
    if (_dataController.text.trim().isEmpty || _horaController.text.trim().isEmpty) {
      return 'Informe data e hora da fiscalização.';
    }
    if (!_vehicleUnknown &&
        (_placaController.text.trim().isEmpty || _marcaController.text.trim().isEmpty)) {
      return 'Informe ao menos placa e marca do veículo, ou marque veículo sem identificação.';
    }
    if (_nomeCondutorController.text.trim().isEmpty ||
        _cpfController.text.trim().isEmpty) {
      return 'Informe nome e CPF do condutor.';
    }
    if (_selectedEnquadramentos.isEmpty) {
      return 'Selecione ao menos um enquadramento.';
    }
    return null;
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.year.toString().padLeft(4, '0')}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  }

  String _formatTime(DateTime date) {
    return '${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          widget.existingDraft == null ? 'Novo CRR' : 'Continuar rascunho',
        ),
        actions: [
          IconButton(
            onPressed: _busy || _submitting ? null : _saveDraft,
            icon: const Icon(Icons.save_outlined),
            tooltip: 'Salvar rascunho',
          ),
        ],
      ),
      body: _busy
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                Container(
                  width: double.infinity,
                  margin: const EdgeInsets.fromLTRB(16, 8, 16, 0),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: colorScheme.primaryContainer,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Preenchimento guiado',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w700,
                            ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Use este fluxo para registrar o atendimento e manter um rascunho local se a conexão oscilar.',
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Stepper(
                    currentStep: _currentStep,
                    onStepTapped: (step) => setState(() => _currentStep = step),
                    onStepContinue: () {
                      if (_currentStep == 2) {
                        _submit();
                        return;
                      }
                      setState(() => _currentStep += 1);
                    },
                    onStepCancel: () {
                      if (_currentStep == 0) {
                        Navigator.of(context).maybePop();
                        return;
                      }
                      setState(() => _currentStep -= 1);
                    },
                    controlsBuilder: (context, details) {
                      return Padding(
                        padding: const EdgeInsets.only(top: 12),
                        child: Row(
                          children: [
                            Expanded(
                              child: FilledButton(
                                onPressed: _submitting ? null : details.onStepContinue,
                                child: Text(
                                  _currentStep == 2
                                      ? (_submitting ? 'Enviando...' : 'Enviar CRR')
                                      : 'Continuar',
                                ),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: OutlinedButton(
                                onPressed: _submitting ? null : details.onStepCancel,
                                child: Text(
                                  _currentStep == 0 ? 'Voltar' : 'Etapa anterior',
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                    steps: [
                      Step(
                        title: const Text('Fiscalização'),
                        isActive: _currentStep >= 0,
                        content: Column(
                          children: [
                            TextField(
                              controller: _numeroController,
                              textCapitalization: TextCapitalization.characters,
                              decoration: const InputDecoration(
                                labelText: 'Número do CRR (opcional)',
                                helperText:
                                    'Se deixar vazio, o servidor gera o próximo número.',
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _localController,
                              decoration: const InputDecoration(
                                labelText: 'Local da fiscalização',
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _municipioController,
                              decoration: const InputDecoration(
                                labelText: 'Município / estado',
                              ),
                            ),
                            const SizedBox(height: 12),
                            Row(
                              children: [
                                Expanded(
                                  child: TextField(
                                    controller: _dataController,
                                    readOnly: true,
                                    onTap: _pickDate,
                                    decoration: const InputDecoration(
                                      labelText: 'Data',
                                      suffixIcon: Icon(Icons.calendar_today_outlined),
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: TextField(
                                    controller: _horaController,
                                    readOnly: true,
                                    onTap: _pickTime,
                                    decoration: const InputDecoration(
                                      labelText: 'Hora',
                                      suffixIcon: Icon(Icons.schedule_outlined),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _medidaController,
                              decoration: const InputDecoration(
                                labelText: 'Medida administrativa',
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _patioController,
                              decoration: const InputDecoration(
                                labelText: 'Local do pátio',
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _placaGuinchoController,
                              textCapitalization: TextCapitalization.characters,
                              decoration: const InputDecoration(
                                labelText: 'Placa do guincho',
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _encarregadoController,
                              decoration: const InputDecoration(
                                labelText: 'Encarregado',
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _observacaoController,
                              minLines: 3,
                              maxLines: 5,
                              decoration: const InputDecoration(
                                labelText: 'Observações operacionais',
                              ),
                            ),
                          ],
                        ),
                      ),
                      Step(
                        title: const Text('Veículo'),
                        isActive: _currentStep >= 1,
                        content: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            SwitchListTile.adaptive(
                              value: _vehicleUnknown,
                              onChanged: (value) {
                                setState(() => _vehicleUnknown = value);
                              },
                              title: const Text('Veículo sem identificação no momento'),
                              subtitle: const Text(
                                'Permite avançar mesmo sem placa ou dados completos.',
                              ),
                              contentPadding: EdgeInsets.zero,
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _placaController,
                              textCapitalization: TextCapitalization.characters,
                              enabled: !_vehicleUnknown,
                              decoration: const InputDecoration(
                                labelText: 'Placa',
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _marcaController,
                              enabled: !_vehicleUnknown,
                              decoration: const InputDecoration(
                                labelText: 'Marca',
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _modeloController,
                              enabled: !_vehicleUnknown,
                              decoration: const InputDecoration(
                                labelText: 'Modelo',
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _corController,
                              enabled: !_vehicleUnknown,
                              decoration: const InputDecoration(
                                labelText: 'Cor',
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _chassiController,
                              textCapitalization: TextCapitalization.characters,
                              enabled: !_vehicleUnknown,
                              decoration: const InputDecoration(
                                labelText: 'Chassi',
                              ),
                            ),
                          ],
                        ),
                      ),
                      Step(
                        title: const Text('Condutor e infrações'),
                        isActive: _currentStep >= 2,
                        content: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            TextField(
                              controller: _nomeCondutorController,
                              decoration: const InputDecoration(
                                labelText: 'Nome do condutor',
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _cpfController,
                              keyboardType: TextInputType.number,
                              decoration: const InputDecoration(
                                labelText: 'CPF do condutor',
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _cnhController,
                              keyboardType: TextInputType.number,
                              decoration: const InputDecoration(
                                labelText: 'CNH',
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _cnhEstrangeiraController,
                              decoration: const InputDecoration(
                                labelText: 'CNH estrangeira',
                              ),
                            ),
                            const SizedBox(height: 16),
                            Text(
                              'AITs',
                              style: Theme.of(context).textTheme.titleMedium,
                            ),
                            const SizedBox(height: 8),
                            Row(
                              children: [
                                Expanded(
                                  child: TextField(
                                    controller: _aitController,
                                    textCapitalization: TextCapitalization.characters,
                                    decoration: const InputDecoration(
                                      labelText: 'Adicionar AIT',
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 12),
                                IconButton.filledTonal(
                                  onPressed: _addAit,
                                  icon: const Icon(Icons.add),
                                ),
                              ],
                            ),
                            if (_aits.isNotEmpty) ...[
                              const SizedBox(height: 8),
                              Wrap(
                                spacing: 8,
                                runSpacing: 8,
                                children: _aits.map((ait) {
                                  return InputChip(
                                    label: Text(ait),
                                    onDeleted: () {
                                      setState(() {
                                        _aits = _aits
                                            .where((current) => current != ait)
                                            .toList();
                                      });
                                    },
                                  );
                                }).toList(),
                              ),
                            ],
                            const SizedBox(height: 16),
                            Text(
                              'Enquadramentos',
                              style: Theme.of(context).textTheme.titleMedium,
                            ),
                            const SizedBox(height: 8),
                            OutlinedButton.icon(
                              onPressed: _enquadramentos.isEmpty
                                  ? null
                                  : _selectEnquadramentos,
                              icon: const Icon(Icons.rule_folder_outlined),
                              label: const Text('Selecionar enquadramentos'),
                            ),
                            const SizedBox(height: 8),
                            Row(
                              children: [
                                Expanded(
                                  child: TextField(
                                    controller: _enquadramentoManualController,
                                    keyboardType: TextInputType.number,
                                    decoration: InputDecoration(
                                      labelText: _enquadramentos.isEmpty
                                          ? 'Código do enquadramento'
                                          : 'Adicionar código manualmente',
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 12),
                                IconButton.filledTonal(
                                  onPressed: _addEnquadramentoManual,
                                  icon: const Icon(Icons.add),
                                ),
                              ],
                            ),
                            if (_selectedEnquadramentos.isNotEmpty) ...[
                              const SizedBox(height: 8),
                              Wrap(
                                spacing: 8,
                                runSpacing: 8,
                                children: _selectedEnquadramentos.map((codigo) {
                                  return InputChip(
                                    label: Text(codigo),
                                    onDeleted: () {
                                      setState(() {
                                        _selectedEnquadramentos =
                                            _selectedEnquadramentos
                                                .where((item) => item != codigo)
                                                .toList();
                                      });
                                    },
                                  );
                                }).toList(),
                              ),
                            ],
                            const SizedBox(height: 20),
                            OutlinedButton.icon(
                              onPressed: _submitting ? null : _saveDraft,
                              icon: const Icon(Icons.cloud_off_outlined),
                              label: const Text('Salvar rascunho local'),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
    );
  }
}
