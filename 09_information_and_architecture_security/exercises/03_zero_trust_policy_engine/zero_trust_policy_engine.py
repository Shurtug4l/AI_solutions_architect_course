from dataclasses import dataclass

@dataclass
class AccessRequest:
    user_id: str
    user_role: str           # e.g. "admin", "user", "guest"
    mfa_ok: bool             # True if MFA verified
    device_trusted: bool     # True if the device is compliant (antivirus, patches, etc.)
    network: str             # e.g. "office", "vpn", "public_wifi"
    resource: str            # resource name
    resource_sensitivity: str  # "low", "medium", "high"
    risk_score: int          # 0-100 (higher = riskier)


class ZeroTrustPolicyEngine:
    def __init__(self):
        # policies could be loaded from a file/config here
        self.max_risk_for_sensitivity = {
            "low": 70,
            "medium": 50,
            "high": 30
        }

    def evaluate(self, request: AccessRequest) -> tuple[bool, list]:
        """
        Returns (decision, reasons)
        decision: True = access granted, False = denied
        reasons: list of explanation strings
        """
        reasons = []

        # 1. Default deny: start from the assumption that access is DENIED
        decision = False
        reasons.append("Default: access denied (Zero Trust principle).")

        # 2. MFA is mandatory
        if not request.mfa_ok:
            reasons.append("MFA not verified: access denied.")
            return False, reasons

        # 3. The device must be trusted/compliant
        if not request.device_trusted:
            reasons.append("Non-compliant device: access denied.")
            return False, reasons

        # 4. No implicit trust from the network
        if request.network == "public_wifi" and request.resource_sensitivity in ("medium", "high"):
            reasons.append("Access from a public network to a sensitive resource: access denied.")
            return False, reasons

        # 5. Risk score check against the resource sensitivity
        max_risk = self.max_risk_for_sensitivity.get(request.resource_sensitivity, 50)
        if request.risk_score > max_risk:
            reasons.append(
                f"Risk score ({request.risk_score}) too high for a {request.resource_sensitivity} resource "
                f"(max allowed: {max_risk})."
            )
            return False, reasons

        # 6. Least privilege: only some roles reach "high" sensitivity resources
        if request.resource_sensitivity == "high" and request.user_role != "admin":
            reasons.append("Only admins can access high-sensitivity resources.")
            return False, reasons

        # If we got here, every check passed
        decision = True
        reasons.append("All Zero Trust checks passed: access granted.")
        return decision, reasons


if __name__ == "__main__":
    engine = ZeroTrustPolicyEngine()

    # Example 1: access GRANTED
    req_ok = AccessRequest(
        user_id="mario",
        user_role="admin",
        mfa_ok=True,
        device_trusted=True,
        network="vpn",
        resource="customers_db",
        resource_sensitivity="high",
        risk_score=20
    )

    decision_ok, reasons_ok = engine.evaluate(req_ok)
    print(f"Request 1 - decision: {'GRANTED' if decision_ok else 'DENIED'}")
    for r in reasons_ok:
        print(" -", r)

    print("\n" + "-"*50 + "\n")

    # Example 2: access DENIED
    req_ko = AccessRequest(
        user_id="luca",
        user_role="user",
        mfa_ok=True,
        device_trusted=True,
        network="public_wifi",
        resource="payroll_db",
        resource_sensitivity="high",
        risk_score=40
    )

    decision_ko, reasons_ko = engine.evaluate(req_ko)
    print(f"Request 2 - decision: {'GRANTED' if decision_ko else 'DENIED'}")
    for r in reasons_ko:
        print(" -", r)
