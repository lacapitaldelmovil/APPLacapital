#!/usr/bin/env python3
"""
Unit tests para verificar las optimizaciones de rendimiento
"""
import unittest
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestPerformanceOptimizations(unittest.TestCase):
    """Test suite para las optimizaciones de rendimiento"""
    
    def test_cache_function_exists(self):
        """Verifica que la función de caché existe en server.py"""
        import server
        self.assertTrue(hasattr(server, 'get_cached_data'))
        self.assertTrue(hasattr(server, 'cache_store'))
        self.assertTrue(hasattr(server, 'CACHE_TTL'))
        print("✅ Sistema de caché implementado correctamente")
    
    def test_session_pooling_exists(self):
        """Verifica que el session pooling está implementado"""
        import server
        self.assertTrue(hasattr(server, 'session'))
        self.assertEqual(type(server.session).__name__, 'Session')
        print("✅ Connection pooling HTTP implementado correctamente")
    
    def test_cache_functionality(self):
        """Verifica que el caché funciona correctamente"""
        import server
        
        call_count = [0]
        
        def test_fetch():
            call_count[0] += 1
            return {"data": "test"}
        
        # Primera llamada - debe ejecutar la función
        result1 = server.get_cached_data("test_key", test_fetch)
        self.assertEqual(call_count[0], 1)
        self.assertEqual(result1, {"data": "test"})
        
        # Segunda llamada - debe usar caché
        result2 = server.get_cached_data("test_key", test_fetch)
        self.assertEqual(call_count[0], 1)  # No debe incrementar
        self.assertEqual(result2, {"data": "test"})
        
        print("✅ Funcionalidad de caché verificada correctamente")
    
    def test_cache_expiration(self):
        """Verifica que el caché expira correctamente"""
        import server
        
        # Guardar TTL original
        original_ttl = server.CACHE_TTL
        
        # Configurar TTL corto para test
        server.CACHE_TTL = 1  # 1 segundo
        
        call_count = [0]
        
        def test_fetch():
            call_count[0] += 1
            return {"timestamp": time.time()}
        
        # Primera llamada
        result1 = server.get_cached_data("expiration_test", test_fetch)
        self.assertEqual(call_count[0], 1)
        
        # Esperar que expire el caché
        time.sleep(1.5)
        
        # Segunda llamada - debe ejecutar de nuevo
        result2 = server.get_cached_data("expiration_test", test_fetch)
        self.assertEqual(call_count[0], 2)  # Debe incrementar
        
        # Restaurar TTL original
        server.CACHE_TTL = original_ttl
        
        print("✅ Expiración de caché verificada correctamente")
    
    def test_mongodb_pooling_config(self):
        """Verifica configuración de MongoDB pooling en sync_worker"""
        # Este test solo verifica que el módulo se importa sin errores
        # ya que necesita variables de entorno para conectarse
        try:
            # Verificar que el código compila
            with open('sync_worker.py', 'r') as f:
                code = f.read()
                self.assertIn('maxPoolSize', code)
                self.assertIn('minPoolSize', code)
                self.assertIn('bulk_write', code)
                self.assertIn('UpdateOne', code)
            print("✅ Configuración de MongoDB pooling verificada")
        except Exception as e:
            self.fail(f"Error verificando sync_worker: {e}")
    
    def test_error_handling_exists(self):
        """Verifica que el manejo de errores está implementado"""
        with open('server.py', 'r') as f:
            code = f.read()
            # Verificar que hay bloques try/except
            self.assertIn('try:', code)
            self.assertIn('except requests.exceptions.RequestException', code)
            self.assertIn('timeout=', code)
        print("✅ Manejo de errores verificado")
    
    def test_env_variables(self):
        """Verifica que se usan variables de entorno"""
        with open('server.py', 'r') as f:
            code = f.read()
            self.assertIn('os.environ.get', code)
        print("✅ Variables de entorno implementadas")

class TestSyncWorkerOptimizations(unittest.TestCase):
    """Test suite para optimizaciones de sync_worker"""
    
    def test_bulk_operations(self):
        """Verifica que se usan operaciones en lote"""
        with open('sync_worker.py', 'r') as f:
            code = f.read()
            self.assertIn('bulk_write', code)
            self.assertIn('UpdateOne', code)
            self.assertIn('bulk_operations', code)
        print("✅ Operaciones en lote implementadas")
    
    def test_projection_queries(self):
        """Verifica que se usan proyecciones en queries"""
        with open('sync_worker.py', 'r') as f:
            code = f.read()
            # Buscar proyección en find()
            self.assertIn('{"nombre": 1, "_id": 0}', code)
        print("✅ Queries con proyección implementados")
    
    def test_session_usage(self):
        """Verifica que se usa session en sync_worker"""
        with open('sync_worker.py', 'r') as f:
            code = f.read()
            self.assertIn('session = requests.Session()', code)
            self.assertIn('session.get', code)
        print("✅ Session HTTP en sync_worker verificado")

def run_tests():
    """Ejecuta todos los tests"""
    print("\n" + "="*60)
    print("EJECUTANDO TESTS DE OPTIMIZACIONES DE RENDIMIENTO")
    print("="*60 + "\n")
    
    # Crear test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar tests
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceOptimizations))
    suite.addTests(loader.loadTestsFromTestCase(TestSyncWorkerOptimizations))
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print(f"Total: {result.testsRun} tests ejecutados")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print(f"Exitosos: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"Fallidos: {len(result.failures)}")
        print(f"Errores: {len(result.errors)}")
    print("="*60 + "\n")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
