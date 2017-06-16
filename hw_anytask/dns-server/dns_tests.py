import subprocess
import unittest
import re

A_TEST = "dig @localhost google.com A"
AAAA_TEST = "dig @localhost google.com AAAA"
NS_TEST = "dig @localhost google.com NS"
MX_TEST = "dig @localhost google.com MX"
SOA_TEST = "dig @localhost google.com SOA"
CNAME_TEST = "dig @localhost google.com CNAME"

EXPECTED_A_TEST_RESULT = [
    "google.com.		43	IN	A	173.194.222.100",
    "google.com.		43	IN	A	173.194.222.113",
    "google.com.		43	IN	A	173.194.222.101",
    "google.com.		43	IN	A	173.194.222.102",
    "google.com.		43	IN	A	173.194.222.138",
]

EXPECTED_AAAA_TEST_RESULT = [
    "google.com.		298	IN	AAAA	2a00:1450:4010:c010::66",
]

EXPECTED_NS_TEST_RESULT = [
    "google.com.		86398	IN	NS	ns1.google.com.",
    "google.com.		86398	IN	NS	ns2.google.com.",
    "google.com.		86398	IN	NS	ns4.google.com.",
    "google.com.		86398	IN	NS	ns3.google.com.",
]

EXPECTED_MX_TEST_RESULT = [
    "google.com.		598	IN	MX	40 alt3.aspmx.l.google.com.",
    "google.com.		598	IN	MX	50 alt4.aspmx.l.google.com.",
    "google.com.		598	IN	MX	10 aspmx.l.google.com.",
    "google.com.		598	IN	MX	20 alt1.aspmx.l.google.com.",
    "google.com.		598	IN	MX	30 alt2.aspmx.l.google.com."
]

EXPECTED_CNAME_TEST_RESULT = [
    "google.com.		21599	IN	CNAME	nginx.usaaa.ru."
]

EXPECTED_SOA_TEST_RESULT = [
    "google.com.		58	IN	SOA	ns3.google.com. dns-admin.google.com. 159226502 900 900 1800 60"
]


class TestStringMethods(unittest.TestCase):
    def test_a_record(self):
        print('Start test: "{}"'.format(A_TEST))
        exact_result = []
        for line in subprocess.check_output(A_TEST.split()).decode().split("\n"):
            if not line.startswith(";"):
                exact_result.append(line)
                print(line)
        self.assertTrue(exact_result, EXPECTED_A_TEST_RESULT)

    def test_aaaa_record(self):
        print('Start test: "{}"'.format(AAAA_TEST))
        exact_result = []
        for line in subprocess.check_output(AAAA_TEST.split()).decode().split("\n"):
            if not line.startswith(";"):
                exact_result.append(line)
                print(line)
        self.assertTrue(exact_result, EXPECTED_AAAA_TEST_RESULT)

    def test_ns_record(self):
        print('Start test: "{}"'.format(NS_TEST))
        exact_result = []
        for line in subprocess.check_output(NS_TEST.split()).decode().split("\n"):
            if not line.startswith(";"):
                exact_result.append(line)
                print(line)
        self.assertTrue(exact_result, EXPECTED_NS_TEST_RESULT)

    def test_mx_record(self):
        print('Start test: "{}"'.format(MX_TEST))
        exact_result = []
        for line in subprocess.check_output(MX_TEST.split()).decode().split("\n"):
            if not line.startswith(";"):
                exact_result.append(line)
                print(line)
        self.assertTrue(exact_result, EXPECTED_MX_TEST_RESULT)

    def test_cname_record(self):
        print('Start test: "{}"'.format(CNAME_TEST))
        exact_result = []
        for line in subprocess.check_output(CNAME_TEST.split()).decode().split("\n"):
            if not line.startswith(";"):
                exact_result.append(line)
                print(line)
        self.assertTrue(exact_result, EXPECTED_CNAME_TEST_RESULT)

    def test_soa_record(self):
        print('Start test: "{}"'.format(SOA_TEST))
        exact_result = []
        for line in subprocess.check_output(SOA_TEST.split()).decode().split("\n"):
            if not line.startswith(";"):
                exact_result.append(line)
                print(line)
        self.assertTrue(exact_result, EXPECTED_SOA_TEST_RESULT)


if __name__ == '__main__':
    unittest.main()
