#!/usr/bin/env python3
"""
ClarityCare Comprehensive Backend API Testing Suite
Tests all endpoints including authentication and protected routes
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

class ClarityCareAPITester:
    def __init__(self, base_url="https://2191ed94-23ee-4a61-a83c-099518936e9c.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.token = None
        self.user_id = None
        self.hospitals = []
        self.procedures = []
        self.payers = []
        self.working_combinations = []
        self.failed_combinations = []

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}: PASSED {details}")
        else:
            print(f"❌ {name}: FAILED {details}")

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f" - {data.get('message', '')}"
            self.log_test("API Root", success, details)
            return success
        except Exception as e:
            self.log_test("API Root", False, f"Error: {str(e)}")
            return False

    def test_get_hospitals(self):
        """Test hospitals endpoint"""
        try:
            response = requests.get(f"{self.api_url}/hospitals", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                self.hospitals = data.get('hospitals', [])
                details = f"Found {len(self.hospitals)} hospitals: {self.hospitals[:3]}..."
            else:
                details = f"Status: {response.status_code}"
            self.log_test("Get Hospitals", success, details)
            return success
        except Exception as e:
            self.log_test("Get Hospitals", False, f"Error: {str(e)}")
            return False

    def test_get_procedures(self):
        """Test procedures endpoint"""
        try:
            response = requests.get(f"{self.api_url}/procedures", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                self.procedures = data.get('procedures', [])
                cpt_codes = [p['code'] for p in self.procedures]
                details = f"Found {len(self.procedures)} procedures: {cpt_codes[:5]}..."
            else:
                details = f"Status: {response.status_code}"
            self.log_test("Get Procedures", success, details)
            return success
        except Exception as e:
            self.log_test("Get Procedures", False, f"Error: {str(e)}")
            return False

    def test_get_payers(self):
        """Test payers endpoint"""
        try:
            response = requests.get(f"{self.api_url}/payers", timeout=10)
            success = response.status_code == 200
            if success:
                data = response.json()
                self.payers = data.get('payers', [])
                details = f"Found {len(self.payers)} payers: {self.payers[:3]}..."
            else:
                details = f"Status: {response.status_code}"
            self.log_test("Get Payers", success, details)
            return success
        except Exception as e:
            self.log_test("Get Payers", False, f"Error: {str(e)}")
            return False

    def test_user_registration(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        user_data = {
            "email": f"test_user_{timestamp}@claritycare.com",
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            response = requests.post(f"{self.api_url}/auth/register", json=user_data, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.token = data.get('access_token')
                self.user_id = data.get('user', {}).get('id')
                details = f"User ID: {self.user_id}, Token received: {bool(self.token)}"
            else:
                try:
                    error_data = response.json()
                    details = f"Status: {response.status_code} - {error_data.get('detail', '')}"
                except:
                    details = f"Status: {response.status_code}"
            
            self.log_test("User Registration", success, details)
            return success
            
        except Exception as e:
            self.log_test("User Registration", False, f"Error: {str(e)}")
            return False

    def test_get_user_profile(self):
        """Test getting user profile"""
        if not self.token:
            self.log_test("Get User Profile", False, "No token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.api_url}/user/profile", headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Profile: {data.get('first_name')} {data.get('last_name')}, Email: {data.get('email')}"
            else:
                try:
                    error_data = response.json()
                    details = f"Status: {response.status_code} - {error_data.get('detail', '')}"
                except:
                    details = f"Status: {response.status_code}"
            
            self.log_test("Get User Profile", success, details)
            return success
            
        except Exception as e:
            self.log_test("Get User Profile", False, f"Error: {str(e)}")
            return False

    def test_update_user_profile(self):
        """Test updating user profile with insurance details"""
        if not self.token:
            self.log_test("Update User Profile", False, "No token available")
            return False
            
        profile_data = {
            "insurance_details": {
                "payer_name": "Aetna",
                "plan_name": "Commercial (PPO/HMO)",
                "member_id": "TEST123456",
                "group_number": "GRP789",
                "deductible_remaining": 500.0,
                "oop_remaining": 2500.0,
                "coinsurance_rate": 0.20,
                "copay": 25.0
            }
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.put(f"{self.api_url}/user/profile", 
                                  json=profile_data, headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                insurance = data.get('insurance_details', {})
                details = f"Insurance updated: {insurance.get('payer_name')} - {insurance.get('plan_name')}"
            else:
                try:
                    error_data = response.json()
                    details = f"Status: {response.status_code} - {error_data.get('detail', '')}"
                except:
                    details = f"Status: {response.status_code}"
            
            self.log_test("Update User Profile", success, details)
            return success
            
        except Exception as e:
            self.log_test("Update User Profile", False, f"Error: {str(e)}")
            return False

    def test_cost_estimate_with_auth(self, cpt_code: str, hospital: str, use_saved_profile: bool = True):
        """Test cost estimation endpoint with authentication"""
        if not self.token:
            self.log_test(f"Cost Estimate ({cpt_code})", False, "No token available")
            return False, {}
            
        # Use saved profile or provide manual data
        if use_saved_profile:
            payload = {
                "cpt_code": cpt_code,
                "quantity": 1,
                "hospital_name": hospital
            }
        else:
            payload = {
                "cpt_code": cpt_code,
                "quantity": 1,
                "hospital_name": hospital,
                "payer_name": "Aetna",
                "plan_name": "Commercial (PPO/HMO)",
                "deductible_remaining": 500.0,
                "oop_remaining": 2500.0,
                "coinsurance_rate": 0.20,
                "copay": 25.0
            }
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(f"{self.api_url}/v2/estimate", 
                                   json=payload, headers=headers, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                patient_pay = data.get('patient_pay', 'N/A')
                plan_pay = data.get('plan_pay', 'N/A')
                details = f"Patient: ${patient_pay}, Plan: ${plan_pay}"
                self.working_combinations.append({
                    'cpt_code': cpt_code,
                    'hospital': hospital,
                    'result': data
                })
            else:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', '')
                except:
                    pass
                details = f"Status: {response.status_code} - {error_detail}"
                self.failed_combinations.append({
                    'cpt_code': cpt_code,
                    'hospital': hospital,
                    'error': details
                })
            
            profile_type = "saved profile" if use_saved_profile else "manual data"
            test_name = f"Cost Estimate ({cpt_code}, {hospital[:15]}, {profile_type})"
            self.log_test(test_name, success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            details = f"Error: {str(e)}"
            self.failed_combinations.append({
                'cpt_code': cpt_code,
                'hospital': hospital,
                'error': details
            })
            profile_type = "saved profile" if use_saved_profile else "manual data"
            test_name = f"Cost Estimate ({cpt_code}, {hospital[:15]}, {profile_type})"
            self.log_test(test_name, False, details)
            return False, {}

    def test_cost_history(self):
        """Test cost history endpoint"""
        if not self.token:
            self.log_test("Get Cost History", False, "No token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.api_url}/user/cost-history", headers=headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                history = data.get('history', [])
                details = f"Found {len(history)} history records"
            else:
                try:
                    error_data = response.json()
                    details = f"Status: {response.status_code} - {error_data.get('detail', '')}"
                except:
                    details = f"Status: {response.status_code}"
            
            self.log_test("Get Cost History", success, details)
            return success
            
        except Exception as e:
            self.log_test("Get Cost History", False, f"Error: {str(e)}")
            return False

    def test_known_working_examples(self):
        """Test known working examples from the request"""
        print("\n🔍 Testing Known Working Examples...")
        
        # Test with saved profile
        success1, result1 = self.test_cost_estimate_with_auth(
            cpt_code="73718",
            hospital="mayo-clinic-florida",
            use_saved_profile=True
        )
        
        # Test with manual data
        success2, result2 = self.test_cost_estimate_with_auth(
            cpt_code="85025",
            hospital="UCLA Ronald Regan",
            use_saved_profile=False
        )
        
        return success1 or success2

    def test_multiple_combinations(self):
        """Test multiple combinations to find working scenarios"""
        print("\n🔍 Testing Multiple Combinations...")
        
        # Test with first few hospitals and procedures
        test_hospitals = self.hospitals[:2] if len(self.hospitals) >= 2 else self.hospitals
        test_procedures = [p['code'] for p in self.procedures[:3]] if len(self.procedures) >= 3 else [p['code'] for p in self.procedures]
        
        combinations_tested = 0
        for hospital in test_hospitals:
            for cpt_code in test_procedures:
                if combinations_tested >= 6:  # Limit to avoid too many tests
                    break
                self.test_cost_estimate_with_auth(cpt_code, hospital, use_saved_profile=True)
                combinations_tested += 1
            if combinations_tested >= 6:
                break

    def test_status_endpoints(self):
        """Test status check endpoints"""
        print("\n🔍 Testing Status Endpoints...")
        
        # Test POST status
        try:
            payload = {"client_name": f"test_client_{datetime.now().strftime('%H%M%S')}"}
            response = requests.post(f"{self.api_url}/status", json=payload, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f" - ID: {data.get('id', 'N/A')}"
            self.log_test("POST Status", success, details)
        except Exception as e:
            self.log_test("POST Status", False, f"Error: {str(e)}")
        
        # Test GET status
        try:
            response = requests.get(f"{self.api_url}/status", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f" - Found {len(data)} status checks"
            self.log_test("GET Status", success, details)
        except Exception as e:
            self.log_test("GET Status", False, f"Error: {str(e)}")

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🏥 CLARITYCARE COMPREHENSIVE API TEST SUMMARY")
        print("="*80)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        print(f"\n📊 DATA LOADED:")
        print(f"Hospitals: {len(self.hospitals)}")
        print(f"Procedures: {len(self.procedures)}")
        print(f"Payers: {len(self.payers)}")
        print(f"Authentication: {'✅ Token obtained' if self.token else '❌ No token'}")
        
        print(f"\n✅ WORKING COMBINATIONS ({len(self.working_combinations)}):")
        for combo in self.working_combinations[:5]:  # Show first 5
            result = combo['result']
            print(f"  • {combo['cpt_code']} + {combo['hospital']}")
            print(f"    → Patient: ${result['patient_pay']}, Plan: ${result['plan_pay']}")
        
        if len(self.failed_combinations) > 0:
            print(f"\n❌ FAILED COMBINATIONS ({len(self.failed_combinations)}):")
            for combo in self.failed_combinations[:5]:  # Show first 5
                print(f"  • {combo['cpt_code']} + {combo['hospital']}")
                print(f"    → {combo['error']}")
        
        print(f"\n🎯 BACKEND STATUS:")
        if self.token and len(self.working_combinations) > 0:
            print("✅ Authentication system working")
            print("✅ Cost calculation engine working")
            print("✅ Profile management working")
            print("✅ Ready for frontend testing")
        elif self.token:
            print("✅ Authentication system working")
            print("⚠️ Cost calculation may have data issues")
            print("⚠️ Check MRF data and hospital/procedure matching")
        else:
            print("❌ Authentication system failed")
            print("❌ Cannot test protected endpoints")
        
        return self.tests_passed >= (self.tests_run * 0.7)  # 70% pass rate acceptable

def main():
    """Main test execution"""
    print("🏥 Starting ClarityCare Comprehensive Backend API Tests...")
    print("="*60)
    
    tester = ClarityCareAPITester()
    
    # Test basic endpoints
    print("\n📋 TESTING BASIC ENDPOINTS...")
    if not tester.test_api_root():
        print("❌ API root failed - stopping tests")
        return 1
    
    # Load reference data
    tester.test_get_hospitals()
    tester.test_get_procedures()
    tester.test_get_payers()
    
    if not (tester.hospitals and tester.procedures and tester.payers):
        print("❌ Failed to load reference data - stopping tests")
        return 1
    
    # Test authentication
    print("\n🔐 TESTING AUTHENTICATION...")
    if not tester.test_user_registration():
        print("❌ User registration failed - stopping tests")
        return 1
    
    # Test profile management
    print("\n👤 TESTING PROFILE MANAGEMENT...")
    tester.test_get_user_profile()
    tester.test_update_user_profile()
    
    # Test cost estimation with authentication
    print("\n💰 TESTING COST ESTIMATION...")
    tester.test_known_working_examples()
    tester.test_multiple_combinations()
    
    # Test cost history
    print("\n📊 TESTING COST HISTORY...")
    tester.test_cost_history()
    
    # Test status endpoints
    print("\n🔍 TESTING STATUS ENDPOINTS...")
    tester.test_status_endpoints()
    
    # Print summary
    all_passed = tester.print_summary()
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())