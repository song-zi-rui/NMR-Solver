#!/usr/bin/env python3
"""
Simple unit test to verify the reactant integration documentation and code structure.

This test validates that the key components for reactant integration are present
and properly documented, without requiring the full dependency stack.

此测试验证反应物集成的关键组件存在且有适当的文档，无需完整的依赖栈。
"""

import ast
import os
import sys

# Get the base directory dynamically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def test_solver_has_candidates_parameter():
    """Test that run_solver has candidates parameter."""
    print("=" * 70)
    print("Test 1: Solver Function Has Candidates Parameter")
    print("测试1：求解器函数有候选参数")
    print("=" * 70)
    
    solver_path = os.path.join(BASE_DIR, 'src', 'core', 'solver.py')
    with open(solver_path, 'r') as f:
        content = f.read()
    
    # Parse the file
    tree = ast.parse(content)
    
    # Find run_solver function
    run_solver = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'run_solver':
            run_solver = node
            break
    
    assert run_solver is not None, "run_solver function not found"
    
    # Check for candidates parameter
    param_names = [arg.arg for arg in run_solver.args.args]
    print(f"Function parameters: {param_names}")
    
    assert 'candidates' in param_names, "candidates parameter not found"
    print("✓ candidates parameter found")
    
    # Check docstring mentions candidates
    docstring = ast.get_docstring(run_solver)
    assert docstring is not None, "Function should have docstring"
    assert 'candidates' in docstring.lower() or 'reactant' in docstring.lower(), \
        "Docstring should mention candidates or reactants"
    print("✓ Docstring documents candidates parameter")
    
    print("\n✓ Test 1 PASSED")
    return True


def test_scene_adaptation_comments():
    """Test that scene adaptation is documented in solver.py."""
    print("\n" + "=" * 70)
    print("Test 2: Scene Adaptation Comments Present")
    print("测试2：场景适配注释存在")
    print("=" * 70)
    
    solver_path = os.path.join(BASE_DIR, 'src', 'core', 'solver.py')
    with open(solver_path, 'r') as f:
        content = f.read()
    
    # Check for scene adaptation comments
    assert '场景适配' in content or 'Scene Adaptation' in content, \
        "Scene adaptation should be mentioned in comments"
    print("✓ Scene adaptation mentioned in comments")
    
    # Check for key functionality description
    assert 'predict_nmr_from_mol(candidates' in content, \
        "Code should predict NMR for candidates"
    print("✓ NMR prediction for candidates present")
    
    assert 'nmr_mol_candidate' in content, \
        "Code should create candidate molecule pool"
    print("✓ Candidate pool creation present")
    
    assert 'add_pool(nmr_mol_candidate)' in content, \
        "Code should integrate candidate pool"
    print("✓ Pool integration present")
    
    print("\n✓ Test 2 PASSED")
    return True


def test_pool_add_method():
    """Test that NMRMolPool has add_pool method with documentation."""
    print("\n" + "=" * 70)
    print("Test 3: Pool Add Method Documented")
    print("测试3：池添加方法已文档化")
    print("=" * 70)
    
    pool_path = os.path.join(BASE_DIR, 'src', 'core', 'pool.py')
    with open(pool_path, 'r') as f:
        content = f.read()
    
    # Parse the file
    tree = ast.parse(content)
    
    # Find add_pool method
    add_pool_method = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'add_pool':
            add_pool_method = node
            break
    
    assert add_pool_method is not None, "add_pool method not found"
    print("✓ add_pool method found")
    
    # Check docstring
    docstring = ast.get_docstring(add_pool_method)
    assert docstring is not None, "add_pool should have docstring"
    assert 'scene' in docstring.lower() or '场景' in docstring, \
        "Docstring should mention scene adaptation"
    print("✓ Docstring mentions scene adaptation")
    
    print("\n✓ Test 3 PASSED")
    return True


def test_config_has_use_candidates():
    """Test that config file has use_candidates option."""
    print("\n" + "=" * 70)
    print("Test 4: Config Has use_candidates Option")
    print("测试4：配置有use_candidates选项")
    print("=" * 70)
    
    config_path = os.path.join(BASE_DIR, 'config', 'demo.yaml')
    with open(config_path, 'r') as f:
        content = f.read()
    
    assert 'use_candidates:' in content, "Config should have use_candidates option"
    print("✓ use_candidates option found")
    
    # Check for comments
    assert '场景适配' in content or 'Scene Adaptation' in content, \
        "Config should have scene adaptation comments"
    print("✓ Scene adaptation comments present")
    
    print("\n✓ Test 4 PASSED")
    return True


def test_analysis_document_exists():
    """Test that analysis document exists and is comprehensive."""
    print("\n" + "=" * 70)
    print("Test 5: Analysis Document Exists")
    print("测试5：分析文档存在")
    print("=" * 70)
    
    doc_path = os.path.join(BASE_DIR, 'REACTANT_INTEGRATION_ANALYSIS.md')
    assert os.path.exists(doc_path), "Analysis document should exist"
    print("✓ Analysis document exists")
    
    with open(doc_path, 'r') as f:
        content = f.read()
    
    # Check for key sections
    required_sections = [
        ('场景适配' in content or 'Scene Adaptation' in content, "Scene adaptation"),
        ('candidates' in content.lower(), "Candidates"),
        ('反应物' in content or 'reactant' in content.lower(), "Reactants"),
        ('核心功能描述' in content or 'Core Feature Description' in content, "Core feature description"),
        ('关键代码组件' in content or 'Key Code Components' in content, "Key code components"),
        ('工作流程' in content or 'Workflow' in content, "Workflow"),
    ]
    
    for condition, section_name in required_sections:
        assert condition, f"Document should contain section: {section_name}"
        print(f"✓ {section_name} section present")
    
    print(f"✓ Document is comprehensive ({len(content)} chars)")
    
    print("\n✓ Test 5 PASSED")
    return True


def test_run_py_loads_candidates():
    """Test that run.py loads candidates from input data."""
    print("\n" + "=" * 70)
    print("Test 6: Run Script Loads Candidates")
    print("测试6：运行脚本加载候选")
    print("=" * 70)
    
    run_path = os.path.join(BASE_DIR, 'run.py')
    with open(run_path, 'r') as f:
        content = f.read()
    
    assert 'candidates = input_data.get("candidates"' in content, \
        "run.py should load candidates from input data"
    print("✓ Candidates loading code present")
    
    assert 'Scene Adaptation' in content or '场景适配' in content, \
        "run.py should have scene adaptation comments"
    print("✓ Scene adaptation comments present")
    
    print("\n✓ Test 6 PASSED")
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("REACTANT INTEGRATION DOCUMENTATION TESTS")
    print("反应物集成文档测试")
    print("=" * 70)
    
    tests = [
        test_solver_has_candidates_parameter,
        test_scene_adaptation_comments,
        test_pool_add_method,
        test_config_has_use_candidates,
        test_analysis_document_exists,
        test_run_py_loads_candidates,
    ]
    
    all_passed = True
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"\n✗ Test FAILED: {e}")
            all_passed = False
        except Exception as e:
            print(f"\n✗ Test ERROR: {e}")
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("ALL TESTS PASSED ✓")
        print("所有测试通过 ✓")
        print("\nThe reactant integration feature is properly documented:")
        print("反应物集成功能已正确文档化：")
        print("  • Candidates parameter in run_solver()")
        print("  • Scene adaptation module in solver.py")
        print("  • Pool integration via add_pool()")
        print("  • Configuration option use_candidates")
        print("  • Comprehensive analysis document")
        print("  • Data loading in run.py")
    else:
        print("SOME TESTS FAILED ✗")
        print("部分测试失败 ✗")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
