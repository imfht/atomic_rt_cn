#!/usr/bin/env python
"""
Simple test script for Atomic Red Team CN application
"""
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from app import app, db
        from models import AttackTechnique, AtomicTest
        from services import AtomicRedTeamService, LLMService
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_database_models():
    """Test database models"""
    print("\nTesting database models...")
    try:
        from app import app, db
        from models import AttackTechnique, AtomicTest
        
        with app.app_context():
            db.create_all()
            
            # Create a test technique
            technique = AttackTechnique(
                technique_id='T9999',
                name='Test Technique',
                description='Test description',
                tactic='Test Tactic',
                platform='Test Platform'
            )
            db.session.add(technique)
            db.session.commit()
            
            # Query it back
            found = AttackTechnique.query.filter_by(technique_id='T9999').first()
            assert found is not None
            assert found.name == 'Test Technique'
            
            # Clean up
            db.session.delete(found)
            db.session.commit()
            
        print("✓ Database models work correctly")
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False


def test_services():
    """Test service classes"""
    print("\nTesting services...")
    try:
        from services import AtomicRedTeamService, LLMService
        
        # Test AtomicRedTeamService
        atomic_service = AtomicRedTeamService('https://example.com')
        techniques = atomic_service.fetch_technique_list()
        assert isinstance(techniques, list)
        
        # Test LLMService
        llm_service = LLMService(api_key='test-key')
        result = llm_service.analyze_technique({
            'technique_id': 'T1234',
            'name': 'Test',
            'description': 'Test desc'
        })
        assert 'summary' in result
        assert 'analysis' in result
        
        print("✓ Services work correctly")
        return True
    except Exception as e:
        print(f"✗ Services test failed: {e}")
        return False


def test_api_endpoints():
    """Test API endpoints"""
    print("\nTesting API endpoints...")
    try:
        from app import app
        
        with app.test_client() as client:
            # Test stats endpoint
            response = client.get('/api/stats')
            assert response.status_code == 200
            data = response.get_json()
            assert 'total_techniques' in data
            
            # Test techniques endpoint
            response = client.get('/api/techniques')
            assert response.status_code == 200
            data = response.get_json()
            assert 'techniques' in data
            
        print("✓ API endpoints work correctly")
        return True
    except Exception as e:
        print(f"✗ API test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("Atomic Red Team CN - Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_database_models,
        test_services,
        test_api_endpoints
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 50)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 50)
    
    return all(results)


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
