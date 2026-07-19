# Data security

## TL;DR

**Cryptography** is the set of methods that obfuscate a message so unauthorized parties cannot read it, an idea that predates computers by centuries (Alberti's cipher disk, the Enigma machine). Modern data security applies it differently depending on where data lives: **encryption at rest** protects stored data (full disk encryption, TDE, file-level encryption; macOS FileVault uses XTS-AES-128) and **encryption in transit** protects data moving over the network (TLS/HTTPS, SSH, VPN, STARTTLS; plain HTTP exposes everything on the path). Passwords get special treatment: they are not encrypted but **hashed**, one-way, with a random **salt** appended so a database breach yields digests instead of credentials. Around the cryptographic core sits **IAM**, the discipline of managing digital identities and access on four pillars: **administration** (identity lifecycle), **authentication** (proving who you are, ideally with more than a password), **authorization** (what that identity may do), and **audit** (verifying the other three actually work). The audit pillar runs on **logs**, the chronological record of who did what and when; a log an attacker can edit is worthless, so log files must be encrypted or permission-locked. The module closes with a log-triage exercise whose lesson generalizes: anomalies surface along four axes, **time, origin, frequency, and privilege**, and the same event weighs more on a privileged account. The stakes are concrete: per IBM X-Force, 30% of cyberattacks involve theft or misuse of valid accounts.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Cryptography** | Methods that make a message unreadable to unauthorized parties | Same goal from Alberti's disk to AES |
| **Encryption at rest** | Protects stored data against unauthorized storage access | Full disk encryption, TDE, file-level encryption |
| **Encryption in transit** | Protects confidentiality and integrity of data moving on the network | TLS/HTTPS, SSH, VPN, STARTTLS |
| **HTTPS vs HTTP** | Same protocol with and without encryption | HTTP traffic is readable by anyone on the path |
| **Hashing** | One-way digest, no way back to the input | Store hash("pippo"), never "pippo" |
| **Salt** | Random string appended before hashing | Same password, different digest per user |
| **IAM** | Create identities, enforce access policy, monitor activity | Authorized users do their job, nothing else |
| **Four pillars of IAM** | Administration, authentication, authorization, audit | Lifecycle, who you are, what you may do, proof it works |
| **Authentication factors** | Password, biometrics, digital certificate for non-humans | MFA and biometrics beat password-only |
| **Log** | Chronological record of system events, written automatically | Timestamp, actor, action, outcome, one line per event |
| **Log integrity** | A log must not be editable by its subjects | Encrypt the file or lock it with OS permissions |
| **Log triage** | Reading logs for anomalies | Time, origin IP, frequency, privilege of the account |
| **OpenPGP / GnuPG** | Public-key standard and its open-source implementation for file encryption | gpg encrypt produces file.txt.gpg |

## From the Alberti disk to Enigma

> Cryptography is the set of methods that make a message "obfuscated" so that it is not comprehensible to unauthorized persons.

The deck opens with two historical anchors. Alberti's cipher disk (15th century) is the first example shown: plaintext in, scrambled text out, readable only by whoever holds the disk setting. The Enigma machine is the industrialized version of the same idea:

> Its complexity came from rotors that changed configuration at every keypress, making messages extremely hard to decode without the correct initial setting.

The history earns its two slides because the structure has not changed: an algorithm everyone can know, a secret setting (the key) that few hold, and security that lives entirely in the key. Enigma fell when the key discipline and the machine's mechanical quirks gave cryptanalysts a foothold, which is still how modern crypto fails in practice: rarely the math, usually the key handling around it.

## Hashing and salting: how passwords are stored

Passwords are the special case where you never want the original back. The deck's example:

```
  # stored in cleartext (bad)
  password = "pippo"

  # stored as a hash digest
  hash("pippo") = Kej23
```

Hash functions named in the slides: MD5, SHA-1, bcrypt. A hash is one-way: from the digest there is no feasible route back to the input. Login verification never decrypts anything, it re-hashes what the user typed and compares digests.

One step further, the **salt**:

> In many cases the algorithm appends a sequence of random characters so that recovering the original sequence is even harder.

```
  hash("pippo" + "djerud234") = cehdheuduxjej
```

The payoff is what a breach yields. An attacker who dumps the database sees "cehdheuduxjej", not "pippo". The salt also breaks precomputation: without it, two users with the same password share a digest and a rainbow table cracks both at once; with a per-user salt, every digest is unique and each password must be attacked individually.

Two precision notes the deck glosses over. First, the slides call this "encrypting" a password, but hashing is not encryption: encryption is reversible by design (whoever holds the key decrypts), hashing is irreversible by design. The distinction matters because it dictates the API: a system that can show you your old password is storing it wrong. Second, of the three algorithms listed only bcrypt belongs in a password store today. MD5 and SHA-1 are cryptographically broken and, worse for this use case, fast: a GPU rig tests billions of MD5 digests per second. bcrypt is deliberately slow and tunable, which is the property you want when the adversary is brute-forcing your dump.

## Encryption at rest and in transit

When does data need encrypting? The deck's answer is: in both places it can live.

```
  DATA AT REST                        DATA IN TRANSIT

  disks, databases, backups          client-server traffic, APIs
        |                                   |
        v                                   v
  full disk encryption               TLS / HTTPS
  TDE (transparent DB encryption)    SSH
  file-level encryption              VPN, STARTTLS
        |                                   |
        v                                   v
  protects against unauthorized      protects confidentiality and
  access to the storage              integrity while moving
```

**At rest** covers archived data: someone steals the disk, snapshots the backup, or reads the database files directly, and finds ciphertext. The concrete example is macOS FileVault, which encrypts the disk with AES in XTS mode (XTS-AES-128), transparently to the user. TDE does the same at the database layer; file-level encryption narrows the scope to individual files.

**In transit** covers network communications between client and server or between services over an API. HTTPS is the canonical case:

> It is the "secure" version of the protocol and guarantees that data is not read along the path between client and server. It is by now a fundamental requirement for any site.

Plain HTTP is the same protocol without the encryption, which means everything it carries is potentially visible to whoever sits on the path: a hostile Wi-Fi access point, a compromised router, a passive sniffer. There is no legitimate reason left to serve anything sensitive over it.

The two categories are separate threat models, not alternatives. Disk encryption does nothing for a request crossing the network; TLS does nothing for the database file on a stolen server. A system is covered only when both are.

## Encrypting files in practice: OpenPGP and GnuPG

The hands-on lesson moves to Linux and file encryption with public-key cryptography.

> OpenPGP (Open Pretty Good Privacy) is an encryption standard for protecting email, files, and data. Based on the PGP software, it was developed to guarantee security, authentication, and integrity of information through public-key cryptography.

GnuPG (gnupg.org) is the open-source implementation of the standard. The demonstrated workflow is the minimal complete loop: install GnuPG, generate a key pair, write the message, encrypt it (producing `Text.txt.gpg`), decrypt it back with the private key. Public-key crypto is what makes the loop practical: the encryption key can circulate freely, only the private key opens the result, so two parties never need to share a secret over a channel that would itself need protecting.

## IAM: who gets in and what they may do

Encryption protects data from outsiders; IAM decides who counts as an insider. The stakes come with a number:

> According to the IBM X-Force Threat Intelligence Index, 30% of cyberattacks involve the theft or misuse of valid accounts.

Nearly a third of attacks do not break the cryptography at all. They log in. That reframes access control from bureaucratic overhead to primary attack surface. The actors to govern are also no longer just people: the deck lists **human users** and **AI agents and bots** side by side, and for this course that second entry is the interesting one, since an agent holding credentials is an identity like any other, with the same lifecycle and the same abuse potential.

> The purpose of IAM is to stop hackers while letting authorized users easily perform the activities they are authorized for, but nothing else.

That "but nothing else" is least privilege in one clause. The discipline rests on four pillars:

- **Administration**: the identity lifecycle. Creating, maintaining, and securely deleting user identities. Also called identity lifecycle management; the deletion half is the one organizations forget, and orphaned accounts of departed employees are a classic entry point.
- **Authentication**: verifying that a user is who they claim to be. The user presents credentials, the authentication factors, and the IAM system checks them against the central database. A human types a password or scans a fingerprint; a non-human actor presents a digital certificate. Factors stack: password-only, biometric, two-or-more-factor. The deck is direct that MFA and biometrics are generally stronger than a password alone, and the X-Force number above explains why: a stolen password without the second factor opens nothing.
- **Authorization**: granting the verified identity the appropriate level of access to a resource. Authentication is the prerequisite: first the system establishes who you are, then it looks up the privileges attached to that identity and grants accordingly. The two are routinely conflated and should not be: authentication answers "who", authorization answers "what".
- **Audit (review)**: verifying that the other three pillars actually work. Monitoring and recording what users do with their access rights, to ensure no one, hackers included, reaches confidential information and that authorized users do not abuse their privileges. The second clause matters: audit watches insiders too.

## Logs: the system's diary

The audit pillar runs on logs.

> A log is a chronological record of events generated automatically by a system, application, or device, storing the actions performed, the errors, and the accesses made.

The deck's image is a digital diary: every time something happens (a user logs in, a file opens, an error fires), the system writes a line saying when, who, and what. Three purposes: monitor system operation, diagnose problems, guarantee security and traceability. A representative format:

```
  2025-10-20T08:15:02Z | alice   | LOGIN_ATTEMPT  | 192.0.2.10   | SUCCESS | "Login via web form"
  2025-10-20T08:17:45Z | bob     | LOGIN_ATTEMPT  | 198.51.100.7 | FAILURE | "Wrong password"
  2025-10-20T09:05:21Z | admin   | PASSWORD_RESET | 203.0.113.5  | SUCCESS | "Reset by admin"
  2025-10-20T11:42:09Z | unknown | LOGIN_ATTEMPT  | 203.0.113.99 | FAILURE | "Unknown user"
```

From lines like these you can see access attempts, spot errors, and recognize intrusion attempts such as brute-force runs. The Python lesson builds exactly this: a script simulating a small management application that writes event strings to a log file.

The lesson's real point is not the writing but the protecting. A log stored as a plain `.txt` is a log any user, malicious or careless, can edit to remove the activity they do not want seen. The deck offers two fixes: encrypt the file, or use OS permissions so only a designated account can modify it. Either way the property being bought is integrity: an audit trail is evidence, and evidence the suspect can rewrite proves nothing.

## Reading logs like an analyst

The closing exercise presents eight log samples from a cloud-hosted company management system and asks which are normal and which deserve investigation. Distilled:

| Log pattern | Reading |
|---|---|
| Successful logins, local IPs, 8 AM | Normal. Regular users, office hours, start of the workday |
| Director logs in at 4:25 AM | Suspicious. Could be legitimate, but why at 4 AM? Possible stolen account |
| Local user, successful login from a Bangkok IP | Suspicious. Either the user is remote-working from Thailand or something is off |
| Unexpected logout, director account | Investigate. Could be accidental, could be worse; ask the user |
| 100 successful logins from one user in 10 seconds | Likely brute force or automation. No human logs in 100 times in 10 seconds |
| Repeated failed logins, same user, same IP | Investigate. Network trouble, forgotten password, or an attack in progress |
| Forced session expiry on the director account | Investigate with extra care: the account likely carries admin privileges |
| Clean logout, local IP, office hours | Normal behavior |

Two generalizations fall out. First, anomalies cluster along four axes: **time** (4 AM vs office hours), **origin** (local subnet vs a foreign IP, checkable via services like ipinfo.io), **frequency** (rates no human produces), and **privilege** (whose account it is). Second, severity is contextual: the exercise deliberately pairs two near-identical events and grades the one on the director's account as more serious, because the blast radius of a compromised admin identity is larger. Log reading is not pattern matching against a blacklist, it is comparing events against a baseline of what normal looks like for this system, this user, this hour.

## Gotchas

- **Calling password hashing "encryption".** Encryption is reversible by whoever holds the key; hashing is one-way by design. A system that can email you your forgotten password is storing it recoverably, which is the failure mode hashing exists to prevent. Reset, never retrieve.
- **Hashing without a salt.** Identical passwords produce identical digests, so one crack breaks every user who chose "123456", and precomputed rainbow tables work at full speed. The salt is cheap and closes both holes.
- **Using fast hashes for passwords.** MD5 and SHA-1 appear in the deck's list but are broken and, decisively, fast. Password hashing wants slow: bcrypt's cost factor exists so that brute-forcing a stolen dump stays expensive as hardware improves.
- **Covering one data state and not the other.** Disk encryption does not protect the API call; TLS does not protect the stolen backup. At rest and in transit are distinct threat models and both need an answer.
- **Logs writable by the users they record.** An editable audit trail is worse than none: it certifies a history the attacker curated. Integrity first, via encryption or OS permissions, or the whole audit pillar is decorative.
- **Treating authentication as authorization.** Proving who you are and being allowed to act are different checks. Systems that grant broad access to anyone authenticated have skipped the pillar where least privilege lives.
- **Forgetting non-human identities.** AI agents and bots hold credentials, accumulate privileges, and get compromised like human accounts. With 30% of attacks running through valid accounts, an ungoverned service identity is an unguarded door.
- **Grading log anomalies without context.** The same event on an intern's account and on the director's account are not the same event. Privilege scales severity; triage that ignores it burns effort on noise and waves through the incident that matters.

## See also

- [01_ai_security_fundamentals.md](01_ai_security_fundamentals.md) - the threat landscape and security goals these controls serve
- [05_critical_asset_protection.md](05_critical_asset_protection.md) - datasets, models, and credentials as the assets encryption and IAM exist to protect
- [06_ai_architecture_security.md](06_ai_architecture_security.md) - where encryption, IAM, and logging sit in a deployed AI architecture
- [08_ai_forensics.md](08_ai_forensics.md) - logs as the raw material of forensic reconstruction; the triage here is the front line of that work
- [../../07_data_governance_knowledge_management/notes/04_data_lifecycle.md](../../07_data_governance_knowledge_management/notes/04_data_lifecycle.md) - the governance view of the same data states this note secures
