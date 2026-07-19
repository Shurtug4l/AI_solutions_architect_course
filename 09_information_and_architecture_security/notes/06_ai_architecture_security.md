# AI architecture security

## TL;DR

**Securing an AI architecture means securing the infrastructure it runs on, not just the model.** The building block is the **container**: an isolated user-space environment that packages an application with its libraries and dependencies while **sharing the host kernel**, which makes it lighter than a VM but also means a kernel compromise likely reaches every container on the host. At scale containers are managed by **orchestrators** (Kubernetes) that schedule, restart, scale, and network fleets of containers, and for AI workloads orchestration buys scalability, efficiency, and more reliable governance. Those workloads land on some mix of **cloud** (IaaS / PaaS / SaaS), **on-premise**, **hybrid**, or **multi-cloud**, each trading control against practicality; AI's compute appetite pushes most organizations toward the cloud whether they like it or not. Securing that surface rests on three levers: picking a provider with adequate guarantees (including where the data physically lives), training the people, and above all adopting **Zero Trust**: never trust any user, device, or application by default, wherever it sits relative to the network perimeter, and grant access per session through dynamic policy per NIST SP 800-207. At the container level the same posture translates into concrete hygiene: non-root processes, signed images, no secrets baked into Dockerfiles, resource limits against local DoS, internal networks, logging.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Container** | Isolated user-space environment with app + dependencies | Docker; virtualizes processes, not hardware |
| **Container vs VM** | VM ships a full guest OS, a container shares the host kernel | Lighter and faster to start, weaker isolation boundary |
| **Kernel sharing limit** | The kernel is the shared single point of failure | Kernel exploit -> likely every container on the host |
| **Orchestrator** | Automated lifecycle management of container fleets | Kubernetes: scheduling, restarts, scaling, load balancing |
| **IaaS / PaaS / SaaS** | Rent infrastructure, a platform, or finished software | VMs and networks vs computing platform vs subscription app |
| **On-premise** | Everything on company-owned servers | Full control, full burden; big-org territory |
| **Hybrid** | On-prem and cloud combined in one flow | Validate locally, process in the provider's cloud |
| **Multi-cloud** | Several providers at once | Exploit different strengths, survive one provider's outage |
| **Zero Trust** | Never trust by default, verify every access | NIST SP 800-207, per-session dynamic policy |
| **Non-root containers** | Container processes run as an unprivileged user | `runAsNonRoot: true`, `USER` in the Dockerfile |
| **Resource limits** | Cap CPU and memory per container | No limits = a local DoS waiting to happen |
| **Secrets hygiene** | Secrets never live in the image | `ENV DB_PASSWORD=...` in a Dockerfile is a leak |

## Containers: isolation without a hypervisor

> A container is a software environment where processes and applications are isolated, virtualizing only user space rather than the entire hardware.

The name is the shipping metaphor taken literally: a box that groups and isolates application code together with everything it needs to run (libraries, frameworks, other dependencies). What is inside one container is invisible to the others.

The slides frame containers as a more efficient and evolved form of virtualization than traditional VMs, then immediately correct the framing, and the correction is the part worth remembering:

- **VMs** virtualize the hardware plus a complete operating system per guest.
- **Containers** virtualize only user space and processes, **sharing the host kernel**.

Not a linear evolution, a lighter and more modern approach with a different isolation boundary:

```
  VIRTUAL MACHINES                     CONTAINERS

  +-------+   +-------+               +-----+  +-----+  +-----+
  |  App  |   |  App  |               | App |  | App |  | App |
  +-------+   +-------+               | deps|  | deps|  | deps|
  | Guest |   | Guest |               +-----+  +-----+  +-----+
  |  OS   |   |  OS   |               +----------------------+
  +-------+   +-------+               |  container runtime   |
  +-------------------+               +----------------------+
  |    hypervisor     |               +----------------------+
  +-------------------+               |  host OS (SHARED     |
  |     host OS       |               |         kernel)      |
  +-------------------+               +----------------------+
  |     hardware      |               |      hardware        |
  +-------------------+               +----------------------+
```

Running in an isolated environment raises the security baseline, and the slides say so. They also flag the limit in the same breath: isolation does not remove the need to evaluate attacks, because if an attacker compromises the kernel, the containers on top of it probably fall with it. That is the practical difference between the two diagrams above: a hypervisor is a hard boundary, namespaces and cgroups are a soft one, and container escape is a recognized attack class precisely because the kernel is shared. Module 06 covered building and shipping containers (see `../../06_AI_services_deployment/notes/`); this section asks the follow-up question, whether what was built would survive an attacker.

## Orchestrators: the conductor for the fleet

The slides open with an orchestra: every component must play the right notes at the right moment. The formal version:

> Orchestration is the coordinated execution of multiple IT automation activities or processes, typically involving several systems, applications, and services, to guarantee that deployment, configuration management, and other processes run in the correct order.

In practice an orchestrator is a platform that manages groups of containers automatically: starting and stopping them on demand, distributing them across servers, monitoring their state and balancing load, handling updates and scaling. The reference implementations named in the deck are Docker for containers and Kubernetes for orchestration.

The worked example makes the need concrete. A web app split into frontend, backend, and database runs fine as three Docker containers on one machine. The moment the requirements grow (run across multiple servers, restart automatically on failure, add backend replicas under load) doing it by hand stops scaling, and the orchestrator takes over: it decides which server runs each container, keeps them alive, spawns new instances when load rises, and manages inter-container communication.

For AI specifically, the slides list what orchestration buys: greater scalability, greater efficiency, better collaboration, improved performance, and more reliable governance and compliance. The governance item deserves its place on the list. An orchestrator is also a policy enforcement point: where workloads run, with what resources, under which security context. That is exactly where several of the controls later in this note get applied.

## Where AI workloads run

Modern applications need serious compute, huge data volumes, and constant availability, which is why they tend to end up in the cloud: the organization stops managing servers and buys a service, keeping only the applications as its problem. The slides call the trade honestly: **less freedom of action in exchange for high practicality**. The service comes in the three canonical grades:

- **IaaS**: the provider rents scalable infrastructure (compute, CPU, RAM, networking, storage) from which the customer builds VMs and base services.
- **PaaS**: the provider supplies a ready computing platform; the customer brings the application.
- **SaaS**: the software is not installed locally at all, it is consumed over the internet, paying for use rather than ownership.

**On-premise** is the opposite pole: applications running locally on company-owned servers, everything built and staffed in-house. It suits large organizations (multinationals) that own data centers and IT personnel, and it trades the cloud's practicality back for control.

Between the poles sit the combinations. **Hybrid** uses both environments in one flow; the deck's example is an access-control system wired to a badge reader, where data is stored and validated on a company server, then shipped to a cloud server that processes payroll. Sensitive raw data stays local, heavy processing goes remote, which is the pattern's whole argument. **Multi-cloud** uses several providers at once, exploiting the strengths of each, with a resilience bonus: if one cloud goes down, the other keeps running.

The AI-shaped conclusion: the cloud gives professionals and small companies resources a local server could never offer, and AI raises the bar further, to the point where on-premise becomes unsustainable for many organizations. The architectural patterns for actually structuring these deployments were module 08's subject (see `../../08_solutions_architectures_design/notes/`); here the concern is what securing them requires.

## Securing cloud-hosted AI: three levers

The deck's recipe for cloud application security has three ingredients, and their ordering is telling:

1. **Choose a cloud with adequate security guarantees**, the slides' example being one located inside the European Economic Area. Provider choice is a security decision before it is a cost decision, and data residency is part of it.
2. **Apply policies like Zero Trust** (next section).
3. **Train the personnel adequately.** The human layer, listed as a peer of the technical ones, which matches where real incidents start.

## Zero Trust

> Zero Trust is a security model based on the principle of never trusting, by default, any user, device, or application, regardless of its position inside or outside the network.

The perimeter model assumed the inside was safe and spent everything on the wall. Zero Trust drops the assumption: the target of protection moves from the network boundary to **users, assets, and resources**, and every access is verified as if it came from a hostile network, because it might.

The slides ground the model in the seven principles from NIST (SP 800-207):

1. All data sources and computing services are considered resources.
2. All communication is secured, regardless of network location.
3. Access to individual enterprise resources is granted on a per-session basis.
4. Access is determined by dynamic policy, including the observable state of client identity, application or service, and the requesting asset, possibly extended with behavioral and environmental attributes.
5. The enterprise monitors and measures the integrity and security posture of all owned and associated assets.
6. All authentication and authorization are dynamic and strictly enforced before access is allowed.
7. The enterprise collects as much information as possible on the current state of assets, network infrastructure, and communications, and uses it to improve its security posture.

Principle 1 is the one that pulls AI systems in: models, feature stores, training data, and inference endpoints are all "data sources and computing services", so they are all resources under Zero Trust policy, not just the databases the model reads from. Principles 3, 4, and 6 together define the enforcement mechanic: no standing access, every session re-evaluated against live signals (identity, device state, context), authorization decided before access, never after.

The course demonstrates the mechanic with a Python policy-engine walkthrough; the hands-on companion lives in [../exercises/03_zero_trust_policy_engine/](../exercises/03_zero_trust_policy_engine/), a minimal engine that evaluates an access request through default deny, mandatory MFA, device compliance, network distrust, a risk-score ceiling scaled to resource sensitivity, and least privilege, returning the full reason list as an audit trail. Small as it is, it encodes the posture faithfully: access is granted only if every check passes, and the default answer is no.

## Hardening a container host: the course checklist

Lesson 6.4 walks through installing Docker on a Linux box (a Raspberry Pi) with security procedures applied at each step, starting from the official documentation rather than a random tutorial, which is itself the first procedure. The checklist:

| Check | Command | Why |
|---|---|---|
| OS up to date | `sudo apt update && sudo apt upgrade` | Unpatched host kernel undermines every container on it |
| Docker up to date | `docker version` | The runtime is attack surface too |
| No useless listening services | `ss -tuln` | Every open port is exposure with no benefit attached |
| Firewall present and active | `sudo ufw status` | Default-deny at the network edge |
| User is not root | `groups` | Daily operation with root privileges amplifies any mistake or exploit |
| Resource limits set | `docker inspect <id> \| grep -E "Memory\|Cpu"` | Prevents a container from starving the host (DoS) |
| Logs available | `docker logs <id>` | No logs, no incident reconstruction |
| Exposed ports known | `docker ps` | Port mappings are the container's actual perimeter |

Nothing exotic, and that is the point: most of container security is host and configuration hygiene applied consistently, not specialized tooling.

## Scenario drill: flaw or not

The section closes with six scenarios to classify. Worth internalizing as a table, because these are the configurations one actually meets in reviews:

| Scenario | Verdict | Why |
|---|---|---|
| Container runs without a specified user, defaulting to root from the image | Flaw | On exploit, the attacker may gain privileges on the host, not just the container |
| Image pulled from Docker Hub, digitally signed by a verified author | Not a flaw (if verified) | Signature guarantees authenticity and integrity of the image |
| `ENV DB_PASSWORD=mysecret123` in the Dockerfile, image pushed to the company registry | Flaw | The secret is visible to anyone with access to the image or the repository |
| New microservice version deployed with no CPU or memory limits | Flaw (local DoS) | An unbounded container can consume all host RAM or CPU |
| Containerized app communicates only over an internal Docker network | Not a flaw (good practice) | Not exposed externally; internal traffic still needs monitoring and inter-container controls |
| Kubernetes deployment sets `securityContext.runAsNonRoot: true` for all containers | Not a flaw (good practice) | Blocks root execution, limiting damage from exploits or container escape |

Two of the "safe" verdicts carry caveats the slides themselves attach, and they generalize. The signed image is safe with respect to tampering, not with respect to content: a verified author can still ship a vulnerable base layer, so signing complements scanning rather than replacing it. The internal network reduces external exposure but says nothing about lateral movement, which is why the note about monitoring internal traffic is there; that caveat is Zero Trust principle 2 restated at container scale. The Dockerfile secret is worse than it looks, too: image layers persist, so deleting the variable in a later layer does not remove it from the earlier one. Secrets belong in runtime injection, never in the build.

## Gotchas

- **Treating container isolation as VM isolation.** Containers share the host kernel; the boundary is namespaces and cgroups, not a hypervisor. A kernel exploit reaches everything on the host, so hardening the host is part of hardening the container.
- **Running containers as root because the image defaults to it.** The default is the flaw: nobody chose root, the Dockerfile just never said otherwise. Set `USER` in the image and `runAsNonRoot: true` in the deployment, and let the platform reject violations.
- **Reading a signature as a security scan.** A verified signature proves who built the image and that it was not tampered with. It proves nothing about the vulnerabilities inside. Sign and scan.
- **Secrets in the Dockerfile.** `ENV` values live in the image layers forever and travel with every pull. The registry becomes a credential distribution service for anyone with read access.
- **Skipping resource limits because the service "is small".** Limits are not a performance tuning knob, they are the blast-radius control for a compromised or misbehaving container. Unbounded equals one bad loop away from a host-wide outage.
- **Assuming the internal network is trusted.** Zero Trust applies inside the cluster too: no external exposure is a good first step, but inter-container traffic still needs controls, or one compromised pod owns the neighborhood.
- **Zero Trust as a product purchase.** It is a policy model: per-session, dynamic, default-deny access decisions across users, devices, and workloads. Buying a gateway without changing the access model changes the invoice, not the posture.

## See also

- [01_ai_security_fundamentals.md](01_ai_security_fundamentals.md) - the threat framing and defense-in-depth baseline this section's controls plug into
- [02_data_security.md](02_data_security.md) - secrets management and data protection, the discipline the Dockerfile-password scenario violates
- [04_classic_threats_in_ai_applications.md](04_classic_threats_in_ai_applications.md) - DoS and privilege escalation as attack classes; here they appear as missing limits and root containers
- [05_critical_asset_protection.md](05_critical_asset_protection.md) - models, data, and endpoints as the critical assets Zero Trust enumerates as resources
