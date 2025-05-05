import os
import json
import datetime
from pathlib import Path

class PolicyUtils:
    """
    Utility class for saving, loading, and managing IAM policies.
    """
    
    def __init__(self, policies_dir="saved_policies"):
        """
        Initialize the PolicyUtils class.
        
        Args:
            policies_dir (str): Directory to store saved policies
        """
        self.policies_dir = policies_dir
        
        # Create the policies directory if it doesn't exist
        os.makedirs(self.policies_dir, exist_ok=True)
    
    def save_policy(self, policy_json, name=None, description=None):
        """
        Save a policy to a JSON file.
        
        Args:
            policy_json (str or dict): The policy JSON as a string or dict
            name (str, optional): Name for the policy file
            description (str, optional): Description of the policy
            
        Returns:
            str: Path to the saved policy file
        """
        try:
            # Parse the policy if it's a string
            if isinstance(policy_json, str):
                policy_dict = json.loads(policy_json)
            else:
                policy_dict = policy_json
            
            # Generate a filename if not provided
            if not name:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                name = f"policy_{timestamp}"
            else:
                # Clean the name to be a valid filename
                name = "".join(c if c.isalnum() or c in ['-', '_'] else '_' for c in name)
            
            # Add metadata
            metadata = {
                "generated_at": datetime.datetime.now().isoformat(),
                "description": description or "Generated IAM policy"
            }
            
            # Create the full data structure
            data = {
                "metadata": metadata,
                "policy": policy_dict
            }
            
            # Save to file
            filename = f"{name}.json"
            filepath = os.path.join(self.policies_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return filepath
        
        except Exception as e:
            print(f"Error saving policy: {str(e)}")
            return None
    
    def load_policy(self, filename):
        """
        Load a policy from a JSON file.
        
        Args:
            filename (str): Name of the policy file
            
        Returns:
            dict: The loaded policy with metadata
        """
        try:
            filepath = os.path.join(self.policies_dir, filename)
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            return data
        
        except Exception as e:
            print(f"Error loading policy: {str(e)}")
            return None
    
    def list_saved_policies(self):
        """
        List all saved policies.
        
        Returns:
            list: List of policy filenames
        """
        try:
            policies = []
            
            for file in os.listdir(self.policies_dir):
                if file.endswith('.json'):
                    policies.append(file)
            
            return policies
        
        except Exception as e:
            print(f"Error listing policies: {str(e)}")
            return []
    
    def extract_and_save_policy(self, text, name=None, description=None):
        """
        Extract a policy from text and save it.
        
        Args:
            text (str): Text containing a JSON policy
            name (str, optional): Name for the policy file
            description (str, optional): Description of the policy
            
        Returns:
            tuple: (success, filepath or error message)
        """
        try:
            # Look for JSON content between triple backticks
            import re
            json_pattern = r"```json\s*([\s\S]*?)\s*```"
            match = re.search(json_pattern, text)
            
            if match:
                json_str = match.group(1).strip()
                # Validate it's proper JSON
                json.loads(json_str)
                filepath = self.save_policy(json_str, name, description)
                return (True, filepath)
            
            # Alternative: look for content that looks like JSON
            json_pattern = r"\{\s*\"Version\"[\s\S]*?\"Statement\"[\s\S]*?\}"
            match = re.search(json_pattern, text)
            
            if match:
                json_str = match.group(0).strip()
                # Validate it's proper JSON
                json.loads(json_str)
                filepath = self.save_policy(json_str, name, description)
                return (True, filepath)
                
            return (False, "No valid policy JSON found in the text")
        
        except json.JSONDecodeError:
            return (False, "Invalid JSON format in the extracted policy")
        except Exception as e:
            return (False, f"Error extracting and saving policy: {str(e)}")
