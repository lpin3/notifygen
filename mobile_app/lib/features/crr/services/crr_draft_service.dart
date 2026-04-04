import 'package:uuid/uuid.dart';

import '../../../core/storage/app_storage.dart';
import '../models/crr_create_payload.dart';
import '../models/crr_draft.dart';
import 'crr_service.dart';

class CrrDraftService {
  CrrDraftService({
    required AppStorage storage,
  }) : _storage = storage;

  final AppStorage _storage;
  final Uuid _uuid = const Uuid();

  Future<List<CrrDraft>> loadDrafts() async {
    final items = await _storage.readPendingDrafts();
    final drafts = items.map(CrrDraft.fromJson).toList()
      ..sort((a, b) => b.savedAt.compareTo(a.savedAt));
    return drafts;
  }

  Future<CrrDraft> saveDraft({
    String? draftId,
    required CrrCreatePayload payload,
    String lastError = '',
  }) async {
    final drafts = await loadDrafts();
    final id = draftId ?? _uuid.v4();
    final updatedDraft = CrrDraft(
      id: id,
      payload: payload,
      savedAt: DateTime.now(),
      lastError: lastError,
    );

    final nextDrafts = drafts.where((draft) => draft.id != id).toList()
      ..insert(0, updatedDraft);
    await _persist(nextDrafts);
    return updatedDraft;
  }

  Future<void> removeDraft(String draftId) async {
    final drafts = await loadDrafts();
    final nextDrafts = drafts.where((draft) => draft.id != draftId).toList();
    await _persist(nextDrafts);
  }

  Future<List<CrrDraft>> syncDrafts(CrrService crrService) async {
    final drafts = await loadDrafts();
    final failed = <CrrDraft>[];

    for (final draft in drafts) {
      try {
        await crrService.criarCrr(draft.payload);
      } catch (error) {
        failed.add(
          draft.copyWith(
            savedAt: DateTime.now(),
            lastError: error.toString().replaceFirst('Exception: ', ''),
          ),
        );
      }
    }

    await _persist(failed);
    return failed;
  }

  Future<void> _persist(List<CrrDraft> drafts) {
    return _storage.writePendingDrafts(
      drafts.map((draft) => draft.toJson()).toList(),
    );
  }
}
