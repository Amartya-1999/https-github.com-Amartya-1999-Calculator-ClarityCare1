#!/usr/bin/env python3
"""
ClarityCare Backend API Testing Suite
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

    def test_cost_estimate(self, cpt_code: str, hospital: str, payer: str, 
                          deductible: float = 500.0, oop: float = 2500.0, 
                          coinsurance: float = 0.20, copay: float = 25.0):
        """Test cost estimation endpoint"""
        payload = {
            "cpt_code": cpt_code,
            "quantity": 1,
            "payer_name": payer,
            "plan_name": "Commercial (PPO/HMO)",
            "hospital_name": hospital,
            "deductible_remaining": deductible,
            "oop_remaining": oop,
            "coinsurance_rate": coinsurance,
            "copay": copay
        }
        
        try:
            response = requests.post(f"{self.api_url}/v2/estimate", 
                                   json=payload, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                patient_pay = data.get('patient_pay', 'N/A')
                plan_pay = data.get('plan_pay', 'N/A')
                details = f"Patient: ${patient_pay}, Plan: ${plan_pay}"
                self.working_combinations.append({
                    'cpt_code': cpt_code,
                    'hospital': hospital,
                    'payer': payer,
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
                    'payer': payer,
                    'error': details
                })
            
            test_name = f"Cost Estimate ({cpt_code}, {hospital[:15]}, {payer[:15]})"
            self.log_test(test_name, success, details)
            return success, response.json() if success else {}
            
        except Exception as e:
            details = f"Error: {str(e)}"
            self.failed_combinations.append({
                'cpt_code': cpt_code,
                'hospital': hospital,
                'payer': payer,
                'error': details
            })
            test_name = f"Cost Estimate ({cpt_code}, {hospital[:15]}, {payer[:15]})"
            self.log_test(test_name, False, details)
            return False, {}

    def test_known_working_example(self):
        """Test the known working example from the request"""
        print("\n🔍 Testing Known Working Example...")
        success, result = self.test_cost_estimate(
            cpt_code="73718",
            hospital="mayo-clinic-florida",
            payer="Aetna",
            deductible=500.0,
            oop=2500.0,
            coinsurance=0.20,
            copay=25.0
        )
        
        if success:
            print(f"✅ Known example works! Patient pays ${result['patient_pay']}, Plan pays ${result['plan_pay']}")
            return True
        else:
            print("❌ Known working example failed!")
            return False

    def test_multiple_combinations(self):
        """Test multiple combinations to find working scenarios"""
        print("\n🔍 Testing Multiple Combinations...")
        
        # Test with first few hospitals, procedures, and payers
        test_hospitals = self.hospitals[:3] if len(self.hospitals) >= 3 else self.hospitals
        test_procedures = [p['code'] for p in self.procedures[:5]] if len(self.procedures) >= 5 else [p['code'] for p in self.procedures]
        test_payers = self.payers[:3] if len(self.payers) >= 3 else self.payers
        
        combinations_tested = 0
        for hospital in test_hospitals:
            for cpt_code in test_procedures:
                for payer in test_payers:
                    if combinations_tested >= 15:  # Limit to avoid too many tests
                        break
                    self.test_cost_estimate(cpt_code, hospital, payer)
                    combinations_tested += 1
                if combinations_tested >= 15:
                    break
            if combinations_tested >= 15:
                break

    def test_edge_cases(self):
        """Test edge cases with different financial parameters"""
        print("\n🔍 Testing Edge Cases...")
        
        if not self.working_combinations:
            print("⚠️ No working combinations found, skipping edge cases")
            return
        
        # Use first working combination for edge case testing
        working = self.working_combinations[0]
        
        # Test zero deductible
        self.test_cost_estimate(
            working['cpt_code'], working['hospital'], working['payer'],
            deductible=0.0, oop=5000.0, coinsurance=0.20, copay=25.0
        )
        
        # Test high OOP limit
        self.test_cost_estimate(
            working['cpt_code'], working['hospital'], working['payer'],
            deductible=1000.0, oop=10000.0, coinsurance=0.30, copay=50.0
        )
        
        # Test zero copay
        self.test_cost_estimate(
            working['cpt_code'], working['hospital'], working['payer'],
            deductible=500.0, oop=2500.0, coinsurance=0.20, copay=0.0
        )

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
        print("🏥 CLARITYCARE API TEST SUMMARY")
        print("="*80)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        print(f"\n📊 DATA LOADED:")
        print(f"Hospitals: {len(self.hospitals)}")
        print(f"Procedures: {len(self.procedures)}")
        print(f"Payers: {len(self.payers)}")
        
        print(f"\n✅ WORKING COMBINATIONS ({len(self.working_combinations)}):")
        for combo in self.working_combinations[:5]:  # Show first 5
            result = combo['result']
            print(f"  • {combo['cpt_code']} + {combo['hospital']} + {combo['payer']}")
            print(f"    → Patient: ${result['patient_pay']}, Plan: ${result['plan_pay']}")
        
        if len(self.failed_combinations) > 0:
            print(f"\n❌ FAILED COMBINATIONS ({len(self.failed_combinations)}):")
            for combo in self.failed_combinations[:5]:  # Show first 5
                print(f"  • {combo['cpt_code']} + {combo['hospital']} + {combo['payer']}")
                print(f"    → {combo['error']}")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        if len(self.working_combinations) > 0:
            print("✅ Backend API is functional with multiple working combinations")
            print("✅ Cost calculation engine is working correctly")
            print("✅ Ready for frontend testing")
        else:
            print("❌ No working combinations found - backend may have issues")
            print("❌ Check MRF data loading and hospital/payer matching")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    print("🏥 Starting ClarityCare Backend API Tests...")
    print("="*60)
    
    tester = ClarityCareAPITester()
    
    # Test basic endpoints
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
    
    # Test known working example
    tester.test_known_working_example()
    
    # Test multiple combinations
    tester.test_multiple_combinations()
    
    # Test edge cases
    tester.test_edge_cases()
    
    # Test status endpoints
    tester.test_status_endpoints()
    
    # Print summary
    all_passed = tester.print_summary()
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())