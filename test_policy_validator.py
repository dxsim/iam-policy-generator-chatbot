#!/usr/bin/env python3
"""
Test script for the PolicyValidator class.

This script tests the functionality of the PolicyValidator class by validating
example policies against best practices.

Usage:
  python test_policy_validator.py
"""

import json
import os
from policy_validator import PolicyValidator

def test_validator():
    """Test the PolicyValidator with various policy examples"""
    validator = PolicyValidator()
    
    # Test cases with expected results
    test_cases = [
        {
            "name": "Valid policy with specific resources",
            "policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetObject",
                            "s3:ListBucket"
                        ],
                        "Resource": [
                            "arn:aws:s3:::specific-bucket",
                            "arn:aws:s3:::specific-bucket/*"
                        ],
                        "Condition": {
                            "StringEquals": {
                                "aws:PrincipalTag/Department": "DataScience"
                            }
                        }
                    }
                ]
            },
            "expected_valid": True
        },
        {
            "name": "Policy with wildcard resource",
            "policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetObject",
                            "s3:ListBucket"
                        ],
                        "Resource": "*"
                    }
                ]
            },
            "expected_valid": False
        },
        {
            "name": "Policy with overly permissive action",
            "policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "s3:*",
                        "Resource": [
                            "arn:aws:s3:::specific-bucket",
                            "arn:aws:s3:::specific-bucket/*"
                        ]
                    }
                ]
            },
            "expected_valid": False
        },
        {
            "name": "Policy missing Version",
            "policy": {
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetObject",
                            "s3:ListBucket"
                        ],
                        "Resource": [
                            "arn:aws:s3:::specific-bucket",
                            "arn:aws:s3:::specific-bucket/*"
                        ]
                    }
                ]
            },
            "expected_valid": False
        }
    ]
    
    # Run tests
    passed = 0
    failed = 0
    
    print("=== Testing PolicyValidator ===\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        
        # Validate the policy
        result = validator.validate_policy(test_case["policy"])
        
        # Check if the result matches the expected outcome
        if result["valid"] == test_case["expected_valid"]:
            print("✅ PASSED")
            passed += 1
        else:
            print("❌ FAILED")
            print(f"  Expected valid: {test_case['expected_valid']}")
            print(f"  Actual valid: {result['valid']}")
            if result["issues"]:
                print("  Issues found:")
                for issue in result["issues"]:
                    print(f"  - {issue}")
            failed += 1
        
        print()
    
    # Test with example policies from the example_policies directory
    if os.path.exists("example_policies"):
        print("=== Testing with example policies ===\n")
        
        for filename in os.listdir("example_policies"):
            if filename.endswith(".json"):
                print(f"Testing {filename}")
                
                try:
                    with open(os.path.join("example_policies", filename), 'r') as f:
                        policy_data = json.load(f)
                    
                    # Extract the policy part
                    if "policy" in policy_data:
                        policy = policy_data["policy"]
                    else:
                        policy = policy_data
                    
                    # Validate the policy
                    result = validator.validate_policy(policy)
                    
                    if result["valid"]:
                        print("✅ Policy is valid according to best practices.")
                        passed += 1
                    else:
                        print("⚠️ Policy has some issues:")
                        for issue in result["issues"]:
                            print(f"  - {issue}")
                        failed += 1
                    
                    print()
                
                except Exception as e:
                    print(f"❌ Error processing {filename}: {str(e)}")
                    failed += 1
                    print()
    
    # Print summary
    print("=== Test Summary ===")
    print(f"Total tests: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    return passed, failed

if __name__ == "__main__":
    test_validator()
