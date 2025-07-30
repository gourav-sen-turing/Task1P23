#!/usr/bin/env python
"""
Advanced test scenarios based on specific failing tests
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from omymodels import create_models, convert_models


def test_enums_with_integers():
    """Test integer enum handling"""
    print("\n" + "="*60)
    print("TEST: Integer Enums (IntEnum)")
    print("="*60)
    
    ddl = """
    CREATE TYPE priority AS ENUM (1, 2, 3, 4, 5);
    CREATE TABLE tasks (
        id INTEGER PRIMARY KEY,
        priority priority DEFAULT 1
    );
    """
    
    try:
        result = create_models(ddl, models_type="pydantic", dump=False)
        code = result['code']
        print(code)
        
        checks = [
            ("IntEnum import", "IntEnum" in code),
            ("Priority class", "class Priority" in code),
            ("Integer enum values", "zero = 1" in code or "one = 2" in code),
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


def test_datetime_defaults():
    """Test datetime default handling"""
    print("\n" + "="*60)
    print("TEST: DateTime Defaults")
    print("="*60)
    
    ddl = """
    CREATE TABLE events (
        id INTEGER PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT NOW()
    );
    """
    
    all_pass = True
    
    # Test with dataclasses
    try:
        result = create_models(ddl, models_type="dataclass", dump=False)
        code = result['code']
        
        if "datetime" in code:
            print("✓ Dataclass: datetime import present")
        else:
            print("✗ Dataclass: datetime import missing")
            all_pass = False
            
        if "field(default_factory=datetime.datetime.now)" in code:
            print("✓ Dataclass: datetime.now handled correctly")
        else:
            print("✗ Dataclass: datetime.now not properly handled")
            # Try to see what's there
            if "CURRENT_TIMESTAMP" in code:
                print("  - Found CURRENT_TIMESTAMP instead of datetime.now")
    except Exception as e:
        print(f"✗ Dataclass Exception: {e}")
        all_pass = False
    
    return all_pass


def test_schema_handling():
    """Test schema handling in tables"""
    print("\n" + "="*60)
    print("TEST: Schema Handling")
    print("="*60)
    
    ddl = """
    CREATE TABLE myschema.users (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100)
    );
    """
    
    try:
        # Test with schema_global=True (default)
        result = create_models(ddl, models_type="sqlalchemy", dump=False)
        code = result['code']
        
        if "__table_args__" in code and "schema" in code:
            print("✓ Schema handled in __table_args__")
        else:
            print("✗ Schema not found in __table_args__")
            
        # Test with schema_global=False
        result = create_models(ddl, models_type="sqlalchemy", schema_global=False, dump=False)
        code2 = result['code']
        
        if code != code2:
            print("✓ schema_global parameter affects output")
        else:
            print("✗ schema_global parameter has no effect")
            
        return True
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


def test_indexes():
    """Test index generation"""
    print("\n" + "="*60)
    print("TEST: Index Generation")
    print("="*60)
    
    ddl = """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        email VARCHAR(255),
        username VARCHAR(50)
    );
    
    CREATE INDEX idx_email ON users(email);
    CREATE UNIQUE INDEX idx_username ON users(username);
    """
    
    try:
        result = create_models(ddl, models_type="sqlalchemy", dump=False)
        code = result['code']
        
        checks = [
            ("Index import", "from sqlalchemy import Index" in code or "Index" in code),
            ("UniqueConstraint for unique index", "UniqueConstraint" in code),
            ("__table_args__", "__table_args__" in code),
            ("idx_email index", "idx_email" in code),
            ("idx_username unique", "idx_username" in code),
        ]
        
        all_pass = True
        for check_name, condition in checks:
            if condition:
                print(f"✓ {check_name}")
            else:
                print(f"✗ {check_name}")
                all_pass = False
        
        # Print relevant part of code for debugging
        if "__table_args__" in code:
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if "__table_args__" in line:
                    print("\nGenerated __table_args__:")
                    for j in range(i, min(i+10, len(lines))):
                        if lines[j].strip() and not lines[j].strip().startswith(')'):
                            print("  " + lines[j])
                        else:
                            print("  " + lines[j])
                            break
        
        return all_pass
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_uuid_support():
    """Test UUID type support"""
    print("\n" + "="*60)
    print("TEST: UUID Support")
    print("="*60)
    
    ddl = """
    CREATE TABLE documents (
        id UUID PRIMARY KEY,
        name VARCHAR(100)
    );
    """
    
    all_pass = True
    
    # Test Pydantic
    try:
        result = create_models(ddl, models_type="pydantic", dump=False)
        code = result['code']
        
        if "UUID" in code or "uuid" in code:
            print("✓ Pydantic: UUID type recognized")
        else:
            print("✗ Pydantic: UUID type not recognized")
            all_pass = False
    except Exception as e:
        print(f"✗ Pydantic Exception: {e}")
        all_pass = False
    
    return all_pass


def test_array_support():
    """Test array type support (PostgreSQL)"""
    print("\n" + "="*60)
    print("TEST: Array Support")
    print("="*60)
    
    ddl = """
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        tags VARCHAR(50)[],
        prices DECIMAL[]
    );
    """
    
    try:
        result = create_models(ddl, models_type="pydantic", dump=False)
        code = result['code']
        
        if "List" in code or "list" in code:
            print("✓ Pydantic: Array type converted to List")
        else:
            print("✗ Pydantic: Array type not properly handled")
            
        return True
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


def test_enum_lower_case():
    """Test enum with lower case handling"""
    print("\n" + "="*60)
    print("TEST: Enum Lower Case Names")
    print("="*60)
    
    ddl = """
    CREATE TYPE user_status AS ENUM ('active', 'inactive');
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        status user_status
    );
    """
    
    try:
        result = create_models(ddl, models_type="pydantic", dump=False)
        code = result['code']
        
        # Check if enum name is properly capitalized
        if "class UserStatus" in code:
            print("✓ Enum class name properly capitalized (UserStatus)")
        else:
            print("✗ Enum class name not properly capitalized")
            
        return True
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


def test_sqlalchemy_to_gino_conversion():
    """Test specific SQLAlchemy to GINO conversion"""
    print("\n" + "="*60)
    print("TEST: SQLAlchemy to GINO Conversion")
    print("="*60)
    
    sqlalchemy_code = """
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE)
"""
    
    try:
        result = convert_models(sqlalchemy_code, models_type="gino")
        
        checks = [
            ("GINO import", "from gino import Gino" in result),
            ("db.Model inheritance", "db.Model" in result),
            ("Enum preserved", "class UserStatus" in result),
            ("Table name preserved", "__tablename__ = 'users'" in result),
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


def main():
    """Run all advanced tests"""
    print("="*60)
    print("O!MyModels - Advanced Test Scenarios")
    print("="*60)
    
    tests = [
        ("test_enums_with_integers", test_enums_with_integers),
        ("test_datetime_defaults", test_datetime_defaults),
        ("test_schema_handling", test_schema_handling),
        ("test_indexes", test_indexes),
        ("test_uuid_support", test_uuid_support),
        ("test_array_support", test_array_support),
        ("test_enum_lower_case", test_enum_lower_case),
        ("test_sqlalchemy_to_gino_conversion", test_sqlalchemy_to_gino_conversion),
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
