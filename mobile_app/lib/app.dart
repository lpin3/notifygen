import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

import 'core/http/api_client.dart';
import 'core/storage/app_storage.dart';
import 'features/auth/presentation/login_page.dart';

class NotifygenMobileApp extends StatefulWidget {
  const NotifygenMobileApp({super.key});

  @override
  State<NotifygenMobileApp> createState() => _NotifygenMobileAppState();
}

class _NotifygenMobileAppState extends State<NotifygenMobileApp> {
  late final AppStorage _storage;
  late final Dio _dio;
  late final ApiClient _apiClient;

  @override
  void initState() {
    super.initState();
    _storage = AppStorage();
    _dio = Dio();
    _apiClient = ApiClient(dio: _dio, storage: _storage);
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Notifygen Mobile',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
        useMaterial3: true,
      ),
      home: LoginPage(
        storage: _storage,
        apiClient: _apiClient,
      ),
    );
  }
}
