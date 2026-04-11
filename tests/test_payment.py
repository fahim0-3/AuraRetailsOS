# ============================================================
# Subsystem: Tests  Pattern: Testing  Role: Test payment functionality
# ============================================================

import unittest
from payment.legacy_stubs import LegacyCreditCardGateway, LegacyDigitalWalletAPI, LegacyUPISystem
from payment.credit_card_adapter import CreditCardAdapter
from payment.digital_wallet_adapter import DigitalWalletAdapter
from payment.upi_adapter import UPIAdapter


class TestPayment(unittest.TestCase):
    def test_legacy_credit_card_gateway(self):
        gateway = LegacyCreditCardGateway()
        result = gateway.authorize(100.0, "token123")
        self.assertTrue(result)
        self.assertIsNotNone(gateway.last_transaction_ref)
        self.assertTrue(gateway.last_transaction_ref.startswith("CC-"))

        result = gateway.reverse_charge(gateway.last_transaction_ref)
        self.assertTrue(result)

    def test_legacy_digital_wallet_api(self):
        api = LegacyDigitalWalletAPI()
        result = api.deduct_balance("wallet123", 50.0)
        self.assertEqual(result, 0)  # 0 = success
        self.assertIsNotNone(api.last_ref)
        self.assertTrue(api.last_ref.startswith("DW-"))

        api.initiate_refund("ref123", 25.0)
        self.assertEqual(api.last_ref, "ref123")

    def test_legacy_upi_system(self):
        upi = LegacyUPISystem()
        result = upi.send_upi_request("vpa@test", 75.0)
        self.assertTrue(result)
        self.assertIsNotNone(upi.last_ref)
        self.assertTrue(upi.last_ref.startswith("UPI-"))

        result = upi.raise_dispute(upi.last_ref)
        self.assertTrue(result)

    def test_credit_card_adapter(self):
        adapter = CreditCardAdapter()
        result = adapter.process_payment(100.0, "user123")
        self.assertTrue(result)
        self.assertIsNotNone(adapter.get_provider_name())

        result = adapter.refund_payment("txn123", 50.0)
        self.assertTrue(result)

    def test_digital_wallet_adapter(self):
        adapter = DigitalWalletAdapter()
        result = adapter.process_payment(75.0, "user456")
        self.assertTrue(result)
        self.assertIsNotNone(adapter.get_provider_name())

        result = adapter.refund_payment("txn456", 25.0)
        self.assertTrue(result)

    def test_upi_adapter(self):
        adapter = UPIAdapter()
        result = adapter.process_payment(60.0, "user789")
        self.assertTrue(result)
        self.assertIsNotNone(adapter.get_provider_name())

        result = adapter.refund_payment("txn789", 20.0)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()