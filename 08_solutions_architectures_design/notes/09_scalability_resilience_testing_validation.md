# Scalability, resilience, testing and validation

## TL;DR

**Scalability** is the system's capacity to absorb growing demand without performance degrading past an acceptable threshold, and in AI systems demand grows along several axes at once: requests, data volume, model complexity, number of models, number of teams. The three scaling modes are **vertical** (bigger machines), **horizontal** (more instances), and **elastic** (automatic adaptation to variable load). **Resilience** is the capacity to keep delivering value when something fails, built from **fault tolerance**, **recovery**, and **graceful degradation**. AI stacks make both harder than classic software: heavy models, latency-critical inference, stateful data pipelines, drift, and GPU costs. The countermeasures are modular cloud-native design plus redundancy, fail-over, observability, and fallbacks. None of it counts until it is tested: an architecture that works in the lab can still fail in production, so validation covers the whole system, not just the model, through five test families (load, resilience/fault-injection, integration, model quality, security/compliance). **Fault injection** is the procedure that turns resilience from a slideware claim into a measured property; **load tests** anchor on **95th percentile latency**; **post-deploy monitoring** watches drift, degradation, and emerging bias so the architecture stays alive over time.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **Scalability** | Absorb more demand without unacceptable degradation | Latency and cost per request stay flat as load grows |
| **Vertical scaling** | More power per component (CPU/GPU, RAM) | Bigger instance type, same instance count |
| **Horizontal scaling** | More parallel components | More replicas behind a load balancer |
| **Elastic scaling** | Automatic adaptation to variable load | Autoscaler adds capacity at peak, sheds it at night |
| **Resilience** | Keep delivering value despite failures | A component dies, users barely notice |
| **Fault tolerance** | Function while part of the resources fail | Redundant inference replicas, no single point of failure |
| **Recovery** | Detect faults and restore state, auto or semi-auto | Failed pipeline restarts itself, state intact |
| **Graceful degradation** | Reduced mode instead of full stop | Fallback answers when the model is unreachable |
| **Fault injection** | Deliberately break things in a test environment | Chaos tools kill a service, you measure recovery |
| **Load test** | Simulate realistic traffic up to peak | JMeter/k6/Locust ramping to the p95 latency target |
| **p95 latency** | Reference percentile for latency budgets | The slowest 5 percent define the user experience |
| **Model quality tests** | Drift, bias, accuracy over time | Monitoring pipeline alerts before users complain |

## Scalability: definition and axes

> Scalability is the capacity of the system to absorb an increase in demand without performance degrading beyond an acceptable threshold.

The definition sounds one-dimensional, but AI systems grow along several axes at the same time:

- number of requests
- volume of data
- computational complexity
- number of models
- number of teams working on the system

The last two are the ones classic capacity planning forgets. A system serving one model to one team scales very differently from a platform serving forty models owned by six teams, even at identical request volume: registry, deployment isolation, and pipeline contention become the bottleneck rather than compute. The symptoms of a scalability problem are always the same pair: latency climbs, and cost per request climbs with it.

### Vertical, horizontal, elastic

```
  Vertical      Horizontal        Elastic
  +------+      +--+ +--+ +--+    load ~~/\~~/\~~
  | BIG  |      |  | |  | |  |    capacity follows:
  | node |      +--+ +--+ +--+      scale out on peaks
  +------+       more instances     scale in when idle
   more power
   per node
```

- **Vertical**: increase the power of individual components (CPU/GPU, RAM). Simple, but bounded by the biggest machine you can buy, and GPUs make that ceiling expensive fast.
- **Horizontal**: increase the number of parallel components (instances, services). This is where stateless inference services shine and stateful pipelines struggle.
- **Elastic**: adapt capacity automatically to variable load. It protects against usage peaks, cuts cost in low-demand periods, and makes system behavior predictable.

The architect's job, per the slides, is to identify where load grows, how it grows, and design each component to absorb it. That per-component framing matters: a system scales like its worst component, and in AI stacks the worst component is rarely the API gateway, it is the feature pipeline or the GPU-bound model server.

## Resilience: surviving failure

> Resilience is the capacity of a system to keep functioning, and keep delivering value, even when something fails.

Designing an AI architecture is not only about working well; it is about deciding what happens when things go wrong. An AI system is many interconnected elements, each of which can fail for its own reasons: network problems, corrupted data, configuration errors, resource saturation, bugs. The slides break resilience into three capabilities, which read as a ladder from best case to acceptable worst case:

```
  fault occurs
      |
      v
  Fault tolerance ----> system keeps working (redundancy absorbs it)
      | not enough
      v
  Recovery ----------> detect + restore state, automatic or semi-automatic
      | not enough
      v
  Graceful degradation -> reduced mode (fallback), never a hard stop
```

- **Fault tolerance**: keep functioning even if part of the resources fails.
- **Recovery**: detect faults and restore state automatically or semi-automatically.
- **Degrade gracefully**: tolerate a reduced mode rather than a complete block.

For AI specifically: models, data pipelines, and inference services all need designed-in emergency paths. A recommendation service that falls back to popularity rankings when the model tier is down is degraded, not broken. That distinction is worth real money during an outage.

## Why AI makes both harder

The slides list the AI-specific challenges, and they compound each other:

- **Data volume and variety**: datasets grow fast and are heterogeneous.
- **Model complexity**: bigger models, longer training, costlier inference.
- **Critical latency**: real-time inference gives the architecture no slack.
- **Data pipelines and feature stores**: complex flows, dependencies, state. State is the enemy of easy horizontal scaling.
- **Continuous change (drift)**: model and data evolve, so the system needs built-in adaptation, not one-off tuning.
- **Costs**: hardware, storage, GPU, cloud spend all become material at scale.
- **Fault management**: pipelines, training jobs, inference, stale models, each failing in its own way.

The through-line: a classic web service mostly scales one stateless tier. An AI system scales a stateful data layer, a compute-hungry training layer, and a latency-critical serving layer simultaneously, while the ground truth underneath (the data distribution) keeps moving. Note 05 covers the lifecycle machinery that handles the moving ground truth; this note is about the architecture that has to survive it.

## Best practices

**For scalability**, the slides converge on modular and cloud-native:

- Modularity: independent components (ingestion, features, inference) scale independently, so you pay for capacity only where load actually grows.
- Cloud-native and elastic resources: serverless, Kubernetes, anything that scales automatically.
- Service-oriented design for AI pipelines (the microservices reasoning from note 02 applied to the ML stack).
- Scalable storage and infrastructure: data lake, object storage (archetypes in note 04).
- Auto-scaling, load balancing, caching for performance.

**For resilience**:

- Redundancy of critical components: inference services, storage, pipelines.
- Fail-over strategies and automatic recovery.
- Observability: metrics, logging, tracing to detect anomalies early.
- Graceful degradation and fallback paths (the reduced mode, designed in advance).
- Resilience testing: fault injection, simulated failures.

That last bullet is the hinge of this whole note. Redundancy and fail-over are configuration; whether they work is an empirical question, and the second half of the note is about answering it.

## Case study: scalable AI infrastructure in cloud

An e-commerce company launches real-time personalized recommendations for tens of millions of users. The design elements the slides pull out:

- cloud data pipeline with storage and a data lake
- microservices for feature extraction and inference, distributed on Kubernetes with auto-scaling
- multi-region redundancy with automatic fail-over
- end-to-end observability: latency, error rate, throughput

Nothing exotic, and that is the point: at this scale the winning design is the boring composition of the best practices above, not a clever bespoke system. This is the same recommender scenario mapped in note 03; here the lens is what keeps it standing at tens of millions of users.

## Checklist and anti-patterns

The operational checklist for judging an architecture:

- Modular, decoupled components?
- Infrastructure auto-scalable or at least provisioned to grow?
- Redundancy and fail-over implemented?
- Complete observability (metrics, logs, tracing)?
- Fallback / graceful degradation plan defined?
- Resilience tests executed (fault injection)?
- Costs under control despite scaling?

The anti-patterns are the checklist inverted: a monolith that cannot scale, a fragile data pipeline, oversized cloud resources without autoscaling (paying peak price for average load), and missing monitoring. Effects: high latency, downtime, out-of-control costs, inability to evolve. Note the checklist item that says "tests executed", not "tests planned". An untested fail-over is a hypothesis, and production is a bad place to test hypotheses.

## Testing the architecture, not just the model

> An AI architecture can work "in the lab" and still fail in production if it is not validated correctly.

Model validation (accuracy on a held-out set) is necessary and wildly insufficient. The unit under test is the whole architecture: pipelines, services, infrastructure, and the model inside them. The slides list five test families:

1. **Load / performance tests**: does the system hold under realistic traffic?
2. **Resilience / fault-injection tests**: does it survive failures?
3. **Integration / end-to-end tests**: do the components work together?
4. **Model quality tests**: drift, bias, accuracy over time.
5. **Security and compliance tests**: covered from the governance side in notes 10 and 11.

For every family the same discipline applies: define the scenario, the metrics, the tools, and the success criteria before running anything. A load test without a pass/fail threshold is a demo, not a test.

## Fault injection: making resilience claims real

This is where the first half of the note gets audited. Every resilience mechanism designed earlier (redundancy, fail-over, fallback) is a claim, and fault injection is the procedure that checks it:

```
  1. Identify critical components (inference service, batch pipeline)
        |
  2. Define fault scenarios (bad inputs, network latency,
        |                     temporary data loss)
  3. Inject faults, controlled, in a test environment
        |
  4. Measure impact: recovery time, error rate,
        |             did the fallback actually fire?
  5. Analyze results -> define improvements -> repeat
```

Step 4 is the one that earns the exercise: "fallback activated" is a boolean you can log, recovery time is a number you can put an SLO on. If the graceful-degradation path never fired during a controlled failure, it will not fire during a real one, and you have learned that for the price of a test run instead of an outage.

## Model quality and post-deploy monitoring

Even when everything around it works, a degrading model can ruin the whole system. The failure modes the slides name:

- **data drift**: the input distribution moves away from training data
- **model degradation**: predictive quality decays over time
- **emerging bias**: skew that was absent or invisible at training time surfaces in production

The answer is quality metrics wired into a monitoring pipeline, so tests do not end at deploy: they become continuous. The slides phrase the goal well: keep the architecture "alive" and functioning over time. Deployment-side monitoring mechanics were covered in module 06, and note 05 places this in the lifecycle loop; the architectural point here is that monitoring is a test that never stops running.

## Tools and environments

- **Load / performance**: JMeter, k6, Locust.
- **Fault injection**: chaos engineering tools (Gremlin, Chaos Monkey).
- **Model quality**: drift detection, bias tests, ML metrics.
- **Environment**: a sandbox or cloud environment separated from production, with synthetic or masked data. Testing on production data in a production environment is how test faults become real incidents, and unmasked data in a test sandbox is a governance problem before it is a technical one (module 07 ground).
- **Logging and monitoring**: collect metrics and traces during tests for post-test analysis. Without capture, a test that fails teaches you nothing.

## Load testing done properly

The best practices for load and performance tests:

- Simulate realistic scenarios: user and event mix, timelines, peaks. Uniform synthetic traffic flatters the system; real traffic is bursty.
- Monitor metrics in real time: latency, throughput, error rate, resource usage.
- Use the **95th percentile as the latency reference**, not the average. Averages hide the tail, and the tail is what the unluckiest 5 percent of users experience; in an inference service that tail is often exactly where GPU queuing lives.
- Analyze bottlenecks: CPU/GPU, memory, network, storage, database.
- Scale progressively: incremental tests up to the peak, so you learn where the system bends before you find where it breaks.

The FastAPI classifier from module 08 exercise 02 is the natural guinea pig here: a containerized inference endpoint is exactly the kind of component you would put under k6, ramp to peak, and read the p95 from.

## Gotchas

- **Elastic scaling treated as a cost feature only.** It is also a resilience feature: a system that cannot shed or add capacity automatically fails harder under a traffic spike than one that degrades its way through it.
- **Redundancy without fail-over testing.** Two replicas that have never been failed over are one replica with extra billing. The checklist item is "fault injection executed", and it is the only line that verifies the others.
- **Average latency as the SLO.** A 200 ms average with a 3 s p95 is a bad service that looks good in reports. Budget on the percentile.
- **Testing only the model.** A 0.95 AUC model inside an untested architecture ships the architecture's failure modes, not the model's accuracy.
- **Monitoring as a post-launch afterthought.** Drift, degradation, and emerging bias are silent by design; nothing crashes, quality just erodes. If the monitoring pipeline is not in the architecture diagram, it will not be in production either.
- **Chaos experiments pointed at production on day one.** The slides say controlled environment, sandbox, synthetic or masked data. Earn the right to test in production later; start where a finding is free.

## See also

- [02_architectural_patterns_for_ai.md](02_architectural_patterns_for_ai.md) - the microservices and event-driven patterns that make horizontal and elastic scaling possible
- [03_from_use_case_to_architecture_diagram.md](03_from_use_case_to_architecture_diagram.md) - the e-commerce recommender case study, from the mapping side
- [05_ai_model_lifecycle_pipeline.md](05_ai_model_lifecycle_pipeline.md) - the lifecycle loop that drift monitoring feeds back into
- [10_enterprise_ready_architectures_and_governance.md](10_enterprise_ready_architectures_and_governance.md) - the security and governance test family, expanded
- [11_compliance_auditing_and_finops.md](11_compliance_auditing_and_finops.md) - the cost axis of the checklist, done as a discipline (FinOps)
- Module 06 notes for the deployment-side view of monitoring, scaling, and serving infrastructure
