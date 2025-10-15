Backend Optimizado para Render - La Capital del Móvil

⚡ OPTIMIZACIONES DE RENDIMIENTO APLICADAS ⚡

Este backend ha sido optimizado para mejorar significativamente el rendimiento:

🚀 MEJORAS PRINCIPALES:
- Sistema de caché en memoria (5 minutos TTL)
- Connection pooling para HTTP y MongoDB
- Operaciones en lote (bulk operations) en MongoDB
- Timeouts y manejo de errores robusto
- Credenciales en variables de entorno

📊 RESULTADOS ESPERADOS:
- 95% reducción en llamadas a API de Square
- 90% reducción en operaciones de MongoDB  
- 5-10x mejora en throughput del servidor
- Tiempos de respuesta de 500-1000ms → 10-50ms (peticiones cacheadas)

📖 Documentación completa en: PERFORMANCE_OPTIMIZATIONS.md

🔧 CONFIGURACIÓN:
1. Copia .env.example a .env
2. Completa las variables de entorno
3. Instala dependencias: pip install -r requirements.txt
4. Ejecuta: python3 server.py

📝 TESTING:
- Ejecuta test_performance.py para verificar mejoras de caché
- Verifica logs de sync_worker para ver operaciones en lote
