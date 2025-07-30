#!/usr/bin/env python
"""
Test file to reproduce all the failing test scenarios mentioned in the issue
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from omymodels import create_models, convert_models
from omymodels.helpers import from_class_to_table_name


def test_helpers_from_class_to_table_name():
    """Test from test_helpers.py::test_from_class_to_table_name"""
    print("\n" + "="*60)
    print("TEST: test_helpers.py::test_from_class_to_table_name")
    print("="*60)
    
    test_cases = [
        ("User", "users"),
        ("Person", "persons"),
        ("Category", "categories"),
        ("City", "cities"),
        ("Company", "companies"),
        ("Baby", "babies"),
        ("Boy", "boys"),  # vowel + y should just add 's'
        ("Day", "days"),  # vowel + y should just add 's'
    ]
    
    all_pass = True
    for class_name, expected in test_cases:
        result = from_class_to_table_name(class_name)
        if result == expected:
            print(f"✓ {class_name} -> {result}")
        else:
            print(f"✗ {class_name} -> Expected: {expected}, Got: {result}")
            all_pass = False
    
    return all_pass


def test_enum_only():
    """Test from test_enum_only.py::test_enum_only"""
    print("\n" + "="*60)
    print("TEST: test_enum_only.py::test_enum_only")
    print("="*60)
    
    ddl = """
    CREATE TYPE user_status AS ENUM ('active', 'inactive', 'banned');
    CREATE TYPE priority AS ENUM ('low', 'medium', 'high');
    """
    
    try:
        result = create_models(ddl, dump=False)
        code = result['code']
        
        checks = [
            ("Enum import present", "from enum import" in code),
            ("UserStatus class present", "class UserStatus" in code),
            ("Priority class present", "class Priority" in code),
            ("String enum inheritance", "(str, Enum)" in code),
        ]
        
        all_pass = True
        for check_name, condition in checks:
            if condition:
                print(f"✓ {check_name}")
            else:
                print(f"✗ {check_name}")
                all_pass = False
        
        if all_pass:
            print("\nGenerated code:")
            print(code)
        
        return all_pass
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enums_in_models():
    """Test enum handling in different model types"""
    print("\n" + "="*60)
    print("TEST: Enums in models (gino, pydantic)")
    print("="*60)
    
    ddl = """
    CREATE TYPE status AS ENUM ('active', 'inactive');
    
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        status status DEFAULT 'active'
    );
    """
    
    all_pass = True
    
    # Test GINO models
    print("\n--- Testing GINO models ---")
    try:
        result = create_models(ddl, models_type="gino", dump=False)
        code = result['code']
        
        if "(str, Enum)" in code:
            print("✓ GINO: String enum has (str, Enum) inheritance")
        else:
            print("✗ GINO: String enum missing proper inheritance")
            all_pass = False
            
        if "class Status" in code:
            print("✓ GINO: Enum class generated")
        else:
            print("✗ GINO: Enum class not found")
            all_pass = False
    except Exception as e:
        print(f"✗ GINO Exception: {e}")
        all_pass = False
    
    # Test Pydantic models
    print("\n--- Testing Pydantic models ---")
    try:
        result = create_models(ddl, models_type="pydantic", dump=False)
        code = result['code']
        
        if "(str, Enum)" in code:
            print("✓ Pydantic: String enum has (str, Enum) inheritance")
        else:
            print("✗ Pydantic: String enum missing proper inheritance")
            all_pass = False
            
        if "class Status" in code:
            print("✓ Pydantic: Enum class generated")
        else:
            print("✗ Pydantic: Enum class not found")
            all_pass = False
    except Exception as e:
        print(f"✗ Pydantic Exception: {e}")
        all_pass = False
    
    return all_pass


def test_dataclasses():
    """Test dataclass generation"""
    print("\n" + "="*60)
    print("TEST: test_dataclasses.py::test_dataclasses")
    print("="*60)
    
    ddl = """
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        price DECIMAL DEFAULT 0.00,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        result = create_models(ddl, models_type="dataclass", dump=False)
        code = result['code']
        
        checks = [
            ("Dataclass import", "from dataclasses import dataclass" in code),
            ("@dataclass decorator", "@dataclass" in code),
            ("Products class", "class Products" in code),
            ("Type annotations", ": int" in code and ": str" in code),
        ]
        
        all_pass = True
        for check_name, condition in checks:
            if condition:
                print(f"✓ {check_name}")
            else:
                print(f"✗ {check_name}")
                all_pass = False
        
        return all_pass
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_convert_models():
    """Test model conversion"""
    print("\n" + "="*60)
    print("TEST: test_converter.py::test_convert_models")
    print("="*60)
    
    sqlalchemy_model = """
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True)
    is_active = Column(Boolean, default=True)
"""
    
    all_pass = True
    
    # Test conversion to Pydantic
    print("\n--- Converting to Pydantic ---")
    try:
        result = convert_models(sqlalchemy_model, models_type="pydantic")
        if "BaseModel" in result and "class User" in result:
            print("✓ Converted to Pydantic successfully")
            if "Optional" in result:
                print("✓ Optional types handled")
        else:
            print("✗ Pydantic conversion incomplete")
            all_pass = False
    except Exception as e:
        print(f"✗ Pydantic conversion failed: {e}")
        all_pass = False
    
    # Test conversion to GINO
    print("\n--- Converting to GINO ---")
    try:
        result = convert_models(sqlalchemy_model, models_type="gino")
        if "db.Model" in result and "class User" in result:
            print("✓ Converted to GINO successfully")
            if "__tablename__ = 'users'" in result:
                print("✓ Table name preserved")
        else:
            print("✗ GINO conversion incomplete")
            all_pass = False
    except Exception as e:
        print(f"✗ GINO conversion failed: {e}")
        all_pass = False
    
    return all_pass


def test_foreign_keys():
    """Test foreign key handling"""
    print("\n" + "="*60)
    print("TEST: Foreign key handling (from multiple test files)")
    print("="*60)
    
    ddl = """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username VARCHAR(50)
    );
    
    CREATE TABLE posts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
        title VARCHAR(200)
    );
    """
    
    all_pass = True
    
    for model_type in ["sqlalchemy", "gino"]:
        print(f"\n--- Testing {model_type} ---")
        try:
            result = create_models(ddl, models_type=model_type, dump=False)
            code = result['code']
            
            if "ForeignKey" in code:
                print(f"✓ {model_type}: ForeignKey found")
                if "users.id" in code:
                    print(f"✓ {model_type}: Correct reference to users.id")
                if "CASCADE" in code or "ondelete" in code:
                    print(f"✓ {model_type}: ON DELETE CASCADE handled")
            else:
                print(f"✗ {model_type}: ForeignKey not found")
                all_pass = False
                
        except Exception as e:
            print(f"✗ {model_type} Exception: {e}")
            all_pass = False
    
    return all_pass


def test_defaults_off():
    """Test defaults_off parameter"""
    print("\n" + "="*60)
    print("TEST: defaults_off parameter")
    print("="*60)
    
    ddl = """
    CREATE TABLE items (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100),
        quantity INTEGER DEFAULT 1,
        active BOOLEAN DEFAULT true
    );
    """
    
    all_pass = True
    
    # Test with defaults
    print("\n--- With defaults ---")
    try:
        result = create_models(ddl, models_type="dataclass", defaults_off=False, dump=False)
        code = result['code']
        default_count = code.count(" = ")
        print(f"✓ Generated with {default_count} default values")
    except Exception as e:
        print(f"✗ Exception: {e}")
        all_pass = False
        return False
    
    # Test without defaults
    print("\n--- Without defaults (defaults_off=True) ---")
    try:
        result = create_models(ddl, models_type="dataclass", defaults_off=True, dump=False)
        code = result['code']
        no_default_count = code.count(" = ")
        print(f"✓ Generated with {no_default_count} default values")
        
        if no_default_count < default_count:
            print("✓ defaults_off parameter works correctly")
        else:
            print("✗ defaults_off parameter not working")
            all_pass = False
    except Exception as e:
        print(f"✗ Exception: {e}")
        all_pass = False
    
    return all_pass


def main():
    """Run all tests"""
    print("="*60)
    print("O!MyModels - Testing Failing Scenarios")
    print("="*60)
    
    tests = [
        ("test_from_class_to_table_name", test_helpers_from_class_to_table_name),
        ("test_enum_only", test_enum_only),
        ("test_enums_in_models", test_enums_in_models),
        ("test_dataclasses", test_dataclasses),
        ("test_convert_models", test_convert_models),
        ("test_foreign_keys", test_foreign_keys),
        ("test_defaults_off", test_defaults_off),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
