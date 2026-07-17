# Edge AI vs cloud AI and cross-industry architectures

## TL;DR

The most physical question in AI architecture: where does the computation run? **Training** almost always lives in the **cloud** (massive GPUs, petabytes, weeks); the real dilemma is **inference**. **Cloud AI** treats the device as a dumb terminal: capture, send over the network, infer on remote GPUs, return JSON. It buys unlimited power, elastic scaling, and trivial deployment, at the price of **network latency**, **data leaving the perimeter**, and per-inference **Opex**. **Edge AI** flips it: the model runs where the data is born (sensor, phone, gateway), giving real-time determinism, **privacy by design**, offline resilience, and bandwidth savings, in exchange for hardware constraints, hard-to-monitor **drift**, and painful fleet updates. Neither wins in general; a decision matrix on connectivity, privacy, model size, latency, and cost picks per case, and the answer in most real systems is **hybrid tiered**: a tiny always-on edge model filters, a massive cloud model reasons on demand. The second half applies this to three regulated industries, and the discriminating variable becomes **where the human sits**. Finance (fraud detection) runs 100% on-premise with **no human in the loop**, because milliseconds do not wait. Healthcare (radiology) runs edge inference with a **human-in-the-loop co-pilot**, because a false negative can cost a life. Manufacturing (visual inspection) runs embedded edge with **deferred HITL**: the operator corrects at end of shift and every correction retrains the model, an **active learning** flywheel. The constraints dictate the architecture, never the other way around.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Training vs inference** | Build the brain vs use the brain | Training: cloud/HPC, ~99% of cases; inference: the dilemma |
| **Cloud AI** | Centralized inference, dumb client | Request/response over API (HTTP/gRPC), GPU on the server |
| **Edge AI** | On-device inference, smart device | Input -> local NPU/CPU -> action, no external call |
| **Edge tiers** | Extreme, mobile, heavy | ESP32 sensor vs smartphone vs industrial gateway / on-prem server |
| **Decision matrix** | Five factors pick the side | Connectivity, privacy, model size, latency, cost model |
| **Tiered (hybrid) architecture** | Edge filters, cloud reasons | Wake-up word pattern; tiny always-on model triggers the big one |
| **VAD + barge-in** | Edge ear that can interrupt the AI | Voice detected in ~10 ms silences TTS before the cloud even knows |
| **The four constraints** | Privacy, latency, cost of error, connectivity | The design questionnaire before any technology choice |
| **HITL** | AI as co-pilot, human decides | Low confidence -> escalate to the expert, prepared for decision |
| **Data flywheel** | Human corrections become training labels | Golden dataset of exactly the hard cases |
| **Finance blueprint** | 100% on-premise, fully automated | Data residency + <10 ms; no human in the blocking path |
| **Health blueprint** | Edge AI + HITL co-pilot | DICOM never leaves the hospital; AI overlays, radiologist decides |
| **Manufacturing blueprint** | Embedded edge + deferred HITL | Camera-level inference; operator validates scraps at end of shift |

## Training vs inference: locate the dilemma first

The first rule before arguing edge vs cloud: the two phases of a model's life have different physics.

- **Training** creates the brain. It needs massive GPU clusters, days to months of compute, petabytes of data. It happens in the cloud or on an HPC cluster in roughly 99% of cases, and nobody seriously debates that.
- **Inference** uses the brain for one prediction. It must be fast (milliseconds) and light, and it is the only phase where "where does it run?" is a genuine architectural decision.

The lecture analogy holds up: training is university, inference is the job. Everything that follows is about inference placement only; the training pipeline itself is note 05 territory.

## Cloud AI: centralized inference

The current default. The device is a **dumb client**, a pure input/output terminal; all intelligence is remote.

```
  Client                Network                 Cloud
  capture data   -->    payload via API   -->   inference on
  (audio, image,        (HTTP / gRPC)           big GPUs
   text)                                          |
  render result  <--    JSON response     <------+
```

Why it wins:

- **Unlimited power**: access to models that will never fit on a phone. If the use case needs a frontier LLM, the placement question answers itself.
- **Elastic scalability**: auto-scaling groups take you from 0 to N users.
- **Easy deployment**: update the server once, every user instantly runs the new version.

Why it hurts:

- **Network latency**: the round-trip time (RTT) is unpredictable, which is disqualifying for strict real-time.
- **Privacy and data sovereignty**: the data leaves the user's or company's perimeter. For medical or financial data this is routinely a compliance wall, not a preference.
- **Operating cost**: every single inference is billed (GPU time plus data transfer). Opex scales with usage forever.

The slide's image of the network as an umbilical cord is accurate: cut the connection and the "smart" product is a brick.

## Edge AI: on-device inference

The inversion: intelligence lives where the data is generated. Flow: input -> local inference (NPU/CPU) -> action, with no external call. "Edge" is broader than the smartphone; the deck slices it into three tiers:

- **Extreme edge**: IoT sensors, microcontrollers (Arduino, ESP32). A vibration sensor on a factory machine.
- **Mobile edge**: smartphones, tablets, wearables.
- **Heavy edge**: industrial gateways, autonomous vehicles, on-premise servers on the factory floor.

What it buys:

- **Real-time response**: no network hop, deterministic timing, which robotics and automotive require. The slide says "zero latency"; read that as zero *network* latency. Local inference still takes time, it is just bounded and predictable, and for a car deciding to brake, bounded beats fast-on-average.
- **Privacy by design**: the data never leaves the device (the FaceID model: your face is not uploaded).
- **Resilience**: offline-first, works without internet.
- **Bandwidth saving**: no gigabytes of video streamed to a server.

What it costs:

- **Hardware constraints**: battery, RAM, thermal budget. The architect fights physics, which is why edge models need aggressive optimization (quantization and similar diets).
- **Model drift**: monitoring real-world performance is hard precisely because the data stays local. The privacy feature and the observability problem are the same fact seen from two sides.
- **Deployment complexity**: updating means an app release or OTA firmware push across a scattered fleet, a logistics nightmare next to redeploying one server.

## The decision matrix

The deck's working tool, worth internalizing verbatim:

| Key factor | Choose cloud if | Choose edge if |
|---|---|---|
| Connectivity | Stable and guaranteed | Intermittent or absent |
| Data privacy | Non-sensitive data | Sensitive data |
| Model size | Massive | Small to medium |
| Latency | Acceptable (>200 ms) | Real-time (<10 ms) |
| Cost model | Pay-as-you-go (Opex) | Hardware upfront (Capex) |

There is no absolute winner, only a dominant constraint per use case: autonomous driving is forced to the edge by latency, a novel-writing assistant is forced to the cloud by model size, health data is pushed to the edge by privacy. The job is balancing the factors, and the honest output of the matrix is often "both", which is the next section.

## Hybrid and tiered architectures

Reality is not binary. The best systems use a **tiered architecture**, and the lecturer's estimate is that this is what you will build in about 80% of real cases.

> Tier 1 (edge): a tiny, always-on, low-power model that filters the noise. Tier 2 (cloud): a massive model, activated only on request, that does the deep analysis. Goal: the reactivity of the edge plus the intelligence of the cloud, at minimum cost.

This is the "wake-up word" pattern, and the deck frames it as fog computing: distribute the computation where it makes economic sense.

```
  data stream --> [ EDGE: tiny always-on model ]
                        |
             99% noise: | discard locally, cost ~0
                        |
                 TRIGGER (something relevant)
                        |
                        v
                  [ CLOUD: massive model ]
                    deep analysis, storage
```

### Example 1: security camera

Streaming video 24/7 to the cloud bankrupts you on bandwidth and storage. The hybrid split: the camera runs a cheap motion + person detection model locally; only when a person is detected does it ship a short clip to the cloud, where a heavy face recognition model (ResNet or transformer class) answers "intruder or owner?". Claimed result: about 99% of bandwidth and cloud cost saved, with cloud-grade accuracy on the clips that matter.

### Example 2: voicebot with barge-in

The most demanding case, because the budget is conversational: respond in under a second and never talk over the user.

- **Edge** (the telephony server or gateway): a **VAD** (voice activity detection) model listens every millisecond, plus a fast local STT (a Whisper Tiny class model) for quick transcription.
- **Trigger and barge-in**: if the VAD hears human voice while the AI is speaking, it cuts the audio in ~10 ms. Waiting for the cloud to notice would mean the bot keeps talking over the caller, which is exactly the behavior that makes voicebots insufferable.
- **Cloud**: the LLM produces the actual answer and a high-fidelity TTS renders the voice.

The division of labor is clean: edge for reactivity (interruptions), cloud for quality (reasoning and voice). The LLM serving side of this stack is note 07.

## Designing under constraints: the four questions

The second deck opens with the thesis that carries the rest: there is no best architecture, only the right architecture for the problem. Four constraints drive every design:

1. **Privacy and compliance** (GDPR, HIPAA): can the data leave the building?
2. **Latency**: milliseconds or minutes?
3. **Cost of error**: if the AI is wrong, how bad is it? Wrong movie recommendation, shrug. Missed fraud or missed tumor, disaster.
4. **Connectivity**: is the network reliable where the system lives?

Do not pick a technology because it is fashionable; pick it because it is the only possible answer to the constraints. Of the four, the deck singles out **cost of error** as the one that decides whether you can automate end to end or must keep a human in the process. The three industry blueprints below are three different resolutions of the same tension: cost of error pulls a human in, latency pushes the human out.

## Human-in-the-loop as an architectural pattern

> HITL is a design pattern in which the AI is not the sole decision maker but acts as a co-pilot for a human expert.

The mechanics are a funnel: the AI does the heavy lifting (millions of transactions or images scanned in seconds), and when its **confidence score** on a case is low it does not guess. It raises its hand and hands the case to the expert, with the evidence already assembled for a fast decision. Three benefits:

- **Risk mitigation**: catastrophic errors get a second pair of eyes before they happen.
- **Operational efficiency**: the expert spends time only on the cases that deserve it.
- **Data flywheel**: every human correction is a high-quality label on precisely the hard cases, feeding a **golden dataset** for retraining. The system gets smarter because of its own mistakes, which is the MLOps loop from note 05 closed by design rather than by afterthought.

The third benefit is the underrated one. Most teams frame HITL as a safety cost; the flywheel framing makes it the cheapest labeling pipeline you will ever run, targeted exactly at your model's weak spots.

## Finance: the fortress, no human in the path

Use case: **fraud detection** on payments. Two iron constraints:

- **Data residency and security**: financial data must never cross the public internet; it stays inside the bank's datacenter.
- **Ultra-low latency**: under 10 ms. Instant payments do not wait for network round trips, let alone for people.

The architecture is **100% on-premise and fully automated**:

```
  +----------------- BANK DATACENTER -----------------+
  |                                                   |
  |  transaction --> core system --> AI engine        |
  |                  (mainframe)     (same rack)      |
  |                        |             |            |
  |                        +--<- verdict-+            |
  |                     approve / block, < 10 ms      |
  +---------------------------------------------------+
                 no clouds in this picture
```

No HITL. The human is simply too slow: seconds against a millisecond budget. The AI is not an assistant here, it is a judge with full authority to kill a transaction, sitting on the same rack as the core banking system for a closed, fast circuit.

The catch, and it is a real one: "no HITL" holds for the synchronous blocking path, which is what the slide is describing. A production fraud stack still wants humans downstream, reviewing blocked transactions and appeals asynchronously, and that review queue is itself a data flywheel. The architectural lesson stands: when the latency budget is milliseconds, the human moves off the critical path; the design choice is where they go instead, not whether they exist.

## Healthcare: the co-pilot

Use case: **medical imaging diagnostics**, an assistant for the radiologist. The constraints invert the finance picture:

- **Privacy and data gravity**: DICOM images are heavy and maximally sensitive (GDPR, HIPAA). They do not leave the hospital's local network.
- **Cost of error as safety**: a false negative, a missed pathology, can cost a life. The AI cannot have the last word.

The architecture is **edge AI plus HITL co-pilot**: inference runs on dedicated on-premise servers (or inside the imaging machine itself), and the output is deliberately not a verdict.

```
  +------------------- HOSPITAL -------------------+
  |                                                |
  |  scanner --> local AI server --> OVERLAY       |
  |  (DICOM)     (edge inference)    (heat map)    |
  |                                     |          |
  |                                     v          |
  |                          RADIOLOGIST (HITL)    |
  |                     reviews, confirms, decides |
  +------------------------------------------------+
          no internet egress for inference
```

The output design is the interesting part. The AI does not emit true/false like the bank's engine; it emits an **overlay**, a heat map on the image. A red mark means "look here more carefully". False alarm, the doctor ignores it; a lesion the doctor had missed, the assistant just earned its keep. Legal responsibility and the final decision stay 100% human. Same life-or-death stakes as finance, opposite HITL placement, and the difference is entirely the latency budget: a radiology read has minutes, a payment has milliseconds.

## Manufacturing: the flywheel

Use case: **visual quality inspection** on a production line. The constraints are physical, not adversarial:

- **Latency under ~20 ms**: the conveyor belt does not stop.
- **Hostile connectivity**: factory-floor internet is often absent or unreliable.

The architecture is **embedded edge AI plus an active learning loop**. Inference runs directly on the camera or on an industrial gateway at the line. The HITL twist is that the human is **deferred**: nobody asks an operator to validate every piece in real time, that would defeat the line's speed. The operator reviews the rejected pieces at end of shift.

```
  PRODUCTION LINE (real time, automated)
  camera --> embedded AI --> robot actuator
                              (keep / reject)
                                   |
                              rejected parts
                                   |
  FEEDBACK LOOP (deferred, human)  v
  operator validates scraps at end of shift
      correct?  -> confirmed label
      AI wrong? -> corrected label
                                   |
                                   v
  local training server: retrain overnight
                                   |
                 updated model --> back to the camera
```

The top half is fast, automatic, unforgiving: camera, AI, robot. The bottom half is where the system improves: every human correction is uploaded to a local training server, the model retrains overnight, and tomorrow's camera is smarter than today's. Scraps become training data. This is the data flywheel from the HITL section made concrete, and it is the cleanest illustration in the module of monitoring and retraining (note 05) surviving in an environment with no cloud connectivity at all.

## The three blueprints side by side

| | Finance | Health | Manufacturing |
|---|---|---|---|
| **Use case** | Fraud detection | Imaging diagnostics | Visual inspection |
| **Dominant constraint** | Latency + data residency | Privacy + cost of error | Latency + connectivity |
| **Placement** | 100% on-premise | Edge (in-hospital servers) | Embedded edge (camera/gateway) |
| **HITL** | None on the blocking path | Synchronous co-pilot | Deferred (end of shift) |
| **AI output** | Binding verdict (block/approve) | Overlay for a human decision | Actuation + labels for retraining |

Read column by column and the pattern-mapping workflow from note 03 reappears: constraints first, pattern second, diagram last. This is exactly the skill the module 08 workshop tests: exercise 04_industry_ai_architecture asks you to take a real industry use case and draw the architecture in draw.io, and these three blueprints are the reference answers to calibrate against. Governance and enterprise-hardening of these designs is note 10; how they scale and fail is note 09.

## Gotchas

- **Debating edge vs cloud for training.** The dilemma is inference-only. Training goes to the cloud or an HPC cluster in ~99% of cases; relitigating that wastes design time.
- **Reading "zero latency" literally.** Edge removes the network RTT and its unpredictability. Local inference still costs time; the win is a bounded, deterministic budget, which is what real-time control actually needs.
- **Treating edge privacy as free observability.** The same property that keeps data on-device makes drift invisible. If the design has no plan for monitoring fleet model quality (proxy metrics, sampled opt-in telemetry, the manufacturing-style deferred loop), the model will rot silently.
- **Binary thinking.** The exam-grade answer to most placement questions is tiered: edge filters and reacts, cloud reasons and stores. Going all-in on one side is usually a sign the decision matrix was skipped.
- **HITL as a checkbox.** Placement is the whole design: synchronous co-pilot (health), off-the-critical-path (finance), deferred batch (manufacturing). "We have a human in the loop" means nothing until you say where the loop is and what latency it can afford.
- **Wasting the corrections.** An HITL system that does not capture human overrides as labeled training data pays for the safety net and forfeits the flywheel. The golden dataset is the return on the human's time; architect the capture path from day one.

## See also

- [02_architectural_patterns_for_ai.md](02_architectural_patterns_for_ai.md) - the batch/streaming and event-driven patterns these placements run on; the camera trigger is event-driven thinking
- [03_from_use_case_to_architecture_diagram.md](03_from_use_case_to_architecture_diagram.md) - the use-case-to-pattern mapping workflow and the diagramming tools (draw.io, C4) the workshop expects
- [05_ai_model_lifecycle_pipeline.md](05_ai_model_lifecycle_pipeline.md) - monitoring, drift, and retraining; the manufacturing loop is that pipeline running air-gapped
- [07_architectures_for_llm_and_generative_ai.md](07_architectures_for_llm_and_generative_ai.md) - the cloud tier of the voicebot (LLM + TTS) in reference-architecture form
- [09_scalability_resilience_testing_validation.md](09_scalability_resilience_testing_validation.md) - what elastic scaling and offline-first resilience mean when tested, not just claimed
- [10_enterprise_ready_architectures_and_governance.md](10_enterprise_ready_architectures_and_governance.md) - governance and security hardening for the regulated blueprints in this note
- exercises/04_industry_ai_architecture - the draw.io workshop where one of these industry architectures gets drawn for real
