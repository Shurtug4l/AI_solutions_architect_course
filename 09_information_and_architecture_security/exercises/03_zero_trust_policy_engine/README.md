# Zero Trust policy engine

Course-provided practice material from section 6 (AI architecture security), translated to English.

A minimal policy engine that evaluates an `AccessRequest` against Zero Trust rules in order: default deny, mandatory MFA, device compliance, no implicit trust from the network, a risk-score ceiling scaled to resource sensitivity, and least privilege on high-sensitivity resources. Every decision returns the full list of reasons, which doubles as an audit trail.

The point of the exercise is the evaluation order and the default-deny posture: access is only granted if every check passes, and the first failing check short-circuits with an explanation.

## Run

```bash
python zero_trust_policy_engine.py
```

Runs two demo requests: an admin on VPN with a compliant device (granted) and a standard user on public wifi targeting a high-sensitivity resource (denied).
