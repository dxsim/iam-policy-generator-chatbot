import json
import re

class PolicyValidator:
    """
    A utility class to validate AWS IAM policies against best practices
    and provide recommendations for improvement.
    """
    
    def __init__(self):
        # Common overly permissive actions that should be flagged
        self.overly_permissive_actions = [
            "*",
            "s3:*",
            "ec2:*",
            "iam:*",
            "dynamodb:*",
            "lambda:*",
            "cloudformation:*"
        ]
        
        # Actions that should be carefully reviewed
        self.sensitive_actions = [
            "iam:CreateUser",
            "iam:CreateRole",
            "iam:PutRolePolicy",
            "iam:AttachRolePolicy",
            "iam:AttachUserPolicy",
            "s3:PutBucketPolicy",
            "ec2:RunInstances",
            "lambda:CreateFunction",
            "kms:Decrypt",
            "secretsmanager:GetSecretValue"
        ]
    
    def validate_policy(self, policy_json):
        """
        Validate an IAM policy and return a list of recommendations.
        
        Args:
            policy_json (str): The policy JSON as a string
            
        Returns:
            dict: Validation results with issues and recommendations
        """
        try:
            # Parse the policy JSON
            if isinstance(policy_json, str):
                policy = json.loads(policy_json)
            else:
                policy = policy_json
                
            # Initialize results
            results = {
                "valid": True,
                "issues": [],
                "recommendations": []
            }
            
            # Check for policy structure
            if "Version" not in policy:
                results["issues"].append("Missing 'Version' field in policy")
                results["recommendations"].append("Add 'Version': '2012-10-17' to the policy")
                results["valid"] = False
                
            if "Statement" not in policy:
                results["issues"].append("Missing 'Statement' field in policy")
                results["valid"] = False
                return results
            
            # Analyze each statement
            statements = policy["Statement"]
            if not isinstance(statements, list):
                statements = [statements]
                
            for i, statement in enumerate(statements):
                # Check for overly permissive actions
                if "Action" in statement:
                    actions = statement["Action"] if isinstance(statement["Action"], list) else [statement["Action"]]
                    
                    for action in actions:
                        if action in self.overly_permissive_actions:
                            results["issues"].append(f"Statement {i+1} contains overly permissive action: {action}")
                            results["recommendations"].append(f"Replace '{action}' with specific actions needed for the use case")
                            results["valid"] = False
                    
                    # Check for sensitive actions
                    for action in actions:
                        if action in self.sensitive_actions:
                            results["issues"].append(f"Statement {i+1} contains sensitive action: {action}")
                            results["recommendations"].append(f"Review if '{action}' is absolutely necessary and consider adding conditions")
                
                # Check for missing resource constraints
                if "Resource" in statement:
                    resources = statement["Resource"] if isinstance(statement["Resource"], list) else [statement["Resource"]]
                    
                    for resource in resources:
                        if resource == "*":
                            results["issues"].append(f"Statement {i+1} applies to all resources ('*')")
                            results["recommendations"].append("Specify exact resource ARNs instead of using '*'")
                            results["valid"] = False
                else:
                    results["issues"].append(f"Statement {i+1} is missing 'Resource' field")
                    results["recommendations"].append("Add specific resource ARNs to the statement")
                    results["valid"] = False
                
                # Check for missing conditions
                if "Condition" not in statement:
                    results["recommendations"].append(f"Consider adding conditions to Statement {i+1} for additional security")
            
            return results
            
        except json.JSONDecodeError:
            return {
                "valid": False,
                "issues": ["Invalid JSON format"],
                "recommendations": ["Check the policy syntax for errors"]
            }
        except Exception as e:
            return {
                "valid": False,
                "issues": [f"Validation error: {str(e)}"],
                "recommendations": ["Review the policy structure"]
            }
    
    def extract_policy_from_text(self, text):
        """
        Extract a JSON policy from a text that may contain other content.
        
        Args:
            text (str): Text that contains a JSON policy
            
        Returns:
            str: Extracted policy JSON or None if not found
        """
        try:
            # Look for JSON content between triple backticks
            json_pattern = r"```json\s*([\s\S]*?)\s*```"
            match = re.search(json_pattern, text)
            
            if match:
                json_str = match.group(1).strip()
                # Validate it's proper JSON
                json.loads(json_str)
                return json_str
            
            # Alternative: look for content that looks like JSON
            json_pattern = r"\{\s*\"Version\"[\s\S]*?\"Statement\"[\s\S]*?\}"
            match = re.search(json_pattern, text)
            
            if match:
                json_str = match.group(0).strip()
                # Validate it's proper JSON
                json.loads(json_str)
                return json_str
                
            return None
        except:
            return None
