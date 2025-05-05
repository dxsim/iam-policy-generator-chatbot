#!/usr/bin/env python3
"""
Policy Viewer Script

This script allows users to view and analyze saved IAM policies.
It can be used to:
1. List all saved policies
2. View a specific policy
3. Validate a policy against best practices

Usage:
  python view_policy.py list
  python view_policy.py view <policy_filename>
  python view_policy.py validate <policy_filename>
"""

import os
import sys
import json
import argparse
from policy_utils import PolicyUtils
from policy_validator import PolicyValidator

def format_policy_json(policy_json):
    """Format policy JSON for better readability"""
    return json.dumps(policy_json, indent=2)

def main():
    parser = argparse.ArgumentParser(description="View and analyze saved IAM policies")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all saved policies")
    
    # View command
    view_parser = subparsers.add_parser("view", help="View a specific policy")
    view_parser.add_argument("filename", help="Policy filename to view")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a policy against best practices")
    validate_parser.add_argument("filename", help="Policy filename to validate")
    
    args = parser.parse_args()
    
    # Initialize utilities
    policy_utils = PolicyUtils()
    policy_validator = PolicyValidator()
    
    # Handle commands
    if args.command == "list":
        policies = policy_utils.list_saved_policies()
        
        if not policies:
            print("No saved policies found.")
            return
        
        print(f"Found {len(policies)} saved policies:")
        for i, policy in enumerate(policies, 1):
            print(f"{i}. {policy}")
    
    elif args.command == "view":
        # Check if the file exists in saved_policies directory
        if not os.path.exists(os.path.join("saved_policies", args.filename)):
            # Check if it exists in example_policies directory
            if os.path.exists(os.path.join("example_policies", args.filename)):
                with open(os.path.join("example_policies", args.filename), 'r') as f:
                    policy_data = json.load(f)
            else:
                print(f"Error: Policy file '{args.filename}' not found.")
                return
        else:
            policy_data = policy_utils.load_policy(args.filename)
        
        if not policy_data:
            print(f"Error: Could not load policy '{args.filename}'.")
            return
        
        # Display policy metadata
        print("\n=== Policy Metadata ===")
        if "metadata" in policy_data:
            for key, value in policy_data["metadata"].items():
                print(f"{key}: {value}")
        
        # Display policy content
        print("\n=== Policy Content ===")
        if "policy" in policy_data:
            print(format_policy_json(policy_data["policy"]))
        else:
            print(format_policy_json(policy_data))
    
    elif args.command == "validate":
        # Check if the file exists in saved_policies directory
        if not os.path.exists(os.path.join("saved_policies", args.filename)):
            # Check if it exists in example_policies directory
            if os.path.exists(os.path.join("example_policies", args.filename)):
                with open(os.path.join("example_policies", args.filename), 'r') as f:
                    policy_data = json.load(f)
            else:
                print(f"Error: Policy file '{args.filename}' not found.")
                return
        else:
            policy_data = policy_utils.load_policy(args.filename)
        
        if not policy_data:
            print(f"Error: Could not load policy '{args.filename}'.")
            return
        
        # Extract the policy part
        if "policy" in policy_data:
            policy = policy_data["policy"]
        else:
            policy = policy_data
        
        # Validate the policy
        validation_results = policy_validator.validate_policy(policy)
        
        # Display validation results
        print("\n=== Policy Validation Results ===")
        
        if validation_results["valid"]:
            print("✅ Policy is valid according to best practices.")
        else:
            print("⚠️ Policy has some issues to address:")
        
        if validation_results["issues"]:
            print("\nIssues:")
            for issue in validation_results["issues"]:
                print(f"- {issue}")
        
        if validation_results["recommendations"]:
            print("\nRecommendations:")
            for rec in validation_results["recommendations"]:
                print(f"- {rec}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
