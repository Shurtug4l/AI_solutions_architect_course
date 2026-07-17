# AI model lifecycle pipeline

## TL;DR

An ML pipeline is not an ETL pipeline with a model bolted on the end. ETL is **deterministic** (same code, same data, same output) and its product is clean data; an ML pipeline is **probabilistic** and its product is a software artifact, the **trained model**, whose value is a performance estimate rather than a guaranteed truth. That shift makes the **MLOps lifecycle** a first-class architectural concern: business and data understanding, data preparation, **training**, **validation**, **deployment**, **monitoring**, and back to the start, because a deployed model is not a finished product. Training turns historical data into a binary artifact, helped by **feature engineering** and disciplined by the **three-set split** (train / validation / test) and **cross-validation**. Validation picks the metric the task actually needs and hunts the number one enemy, **overfitting**. Deployment first slims the model (**pruning**, **quantization**, **ONNX**) and then chooses between two serving patterns, **batch** (throughput and cost) and **real-time** (latency and availability). Monitoring closes the loop: **data drift** and **concept drift** degrade performance (**model drift**), and drift triggers automated **retraining**. Traditional software is written once; a model is cultivated continuously, and the architecture has to be designed for that loop from day one.

## Cheatsheet

| Concept | One-line | Practical signal |
|---|---|---|
| **ETL vs ML pipeline** | Data-moving vs model-producing | ETL output: clean tables; ML output: a model artifact |
| **MLOps lifecycle** | Understand, prepare, train, validate, deploy, monitor, repeat | A circle, not a line ending at deployment |
| **Training** | Algorithm learns input-output relations from history | Output is a binary file (e.g. `.pkl`), not a report |
| **Feature engineering** | Domain knowledge encoded as new columns | Price/sqm from price and area, BMI from weight and height |
| **Three-set split** | Train (~70) / validation (~15) / test (~15) | Test set locked away, used exactly once |
| **Data leakage** | Test data influences training decisions | Lab-brilliant model that collapses in production |
| **Cross-validation** | K rotating validation folds, judge on the mean | Model good on 5 folds, not lucky on 1 |
| **Overfitting** | Memorising training data, noise included | 99% train accuracy, 60% test accuracy |
| **Model optimization** | Pruning, quantization, ONNX export | Smaller, faster artifact before it ships |
| **Batch deployment** | Parallel bulk inference, no user waiting | Spot instances, servers at 100% then off |
| **Real-time deployment** | Model behind an always-on API | Millisecond answers, SLA, autoscaling |
| **Data drift** | Input statistics shift vs training data | Summer-trained model fed winter behaviour |
| **Concept drift** | Same inputs, changed meaning | Bulk mask purchase: doctor in 2018, anyone in 2020 |
| **Model drift** | Measured performance decay, the symptom | Accuracy chart trending down in production |
| **Retraining trigger** | Metric threshold or input-distribution divergence | Pipeline retrains, validates, swaps automatically |

## Two pipelines, two contracts

The starting distinction the deck insists on, and rightly so:

| Pipeline | Goal | Actors | Output | Focus |
|---|---|---|---|---|
| **ETL** | Move and clean data | Data engineers, analysts | Clean data in a DB or warehouse | Data |
| **ML** | Create and automate a model | Data scientists, ML engineers | A model or a service | Model |

The deeper difference is the contract each pipeline offers. ETL is deterministic: run it today or tomorrow on the same data and the result is identical, so its quality question is consistency. An ML pipeline produces an estimate, not a truth; machine learning is probabilistic, so the quality question becomes prediction performance. Architecturally this matters because the two pipelines fail differently: an ETL bug corrupts data and is caught by reconciliation, a model degradation corrupts decisions silently until someone measures it. That is why the lifecycle below ends in monitoring rather than in a handover. The ETL side of the story, including the hands-on build, is exercise 01 (data pipeline with Python) and note 04 on data foundations.

## The lifecycle is a loop

Six stages, and the arrow out of the last one points back at the first:

```
  Business & Data     Data            Model          Evaluation
  Understanding  -->  Preparation --> Training  -->  & Validation
        ^             (ETL)                               |
        |                                                 v
        +--------  Monitoring  <-------------------  Deployment
                   drift detection,                  batch / real-time
                   fresh data for retraining
```

This is DevOps applied to machine learning, which is where the name MLOps comes from. The structural insight worth internalising as an architect: traditional software is written once and runs until requirements change; a model starts degrading the moment it touches the real world, because the world moves and the training data does not. Production is where the real work begins, since monitoring harvests the fresh data that feeds the next training round. Designing the architecture as a straight line to deployment therefore bakes in obsolescence: the retraining path, the data capture at inference time, and the model swap mechanism have to exist in the design even if the first version never uses them. The engineering machinery that implements this loop (CI/CD, registries, serving stacks) is covered in depth in module 06 notes; here the concern is that the loop shapes the architecture itself.

## Phase 1: training

> Training is the process in which the algorithm analyses historical data to learn the relations between inputs and outputs, with the goal of finding hidden patterns to predict on future, unseen data.

The point the deck hammers, and it is a good habit to keep: the output of training is not a report or a chart. It is a concrete software artifact, typically a binary file such as a `.pkl` in Python, that contains everything the model extracted from the data. That file is what gets versioned, moved, optimized, and served. Treating the model as an artifact with a lifecycle of its own is what makes the model registry (note 06) a natural next step.

### Feature engineering

Feature engineering is domain knowledge turned into columns: creating information the model would otherwise have to guess at. The deck's examples are compact and telling. Real estate: from price and square meters, derive price per square meter. Health: from weight and height, derive BMI. Handing the model BMI is handing it a "super-clue" backed by medical science, instead of hoping it rediscovers the ratio on its own.

The boundary the deck draws is worth remembering. This artisanal work pays off on tabular business data, where human insight routinely beats raw compute. On unstructured data (images, audio) humans cannot write features by hand, there is no clean formula for the curve of a nose, so deep learning extracts features itself. Knowing which side of that boundary a use case sits on is an early architectural decision: it drives the model family, the hardware bill, and how much data-science craft the project needs.

### The three-set split

To train and validate honestly, the data splits three ways, not two:

- **Training set** (~70%): the textbook the model studies on.
- **Validation set** (~15%): the mock exams, used for tuning, choosing hyperparameters and model complexity without burning the final test.
- **Test set** (~15%): data in the vault, used exactly once for the final grade.

The golden rule: lock the test set away immediately and never let it influence any decision, not feature selection, not model choice, nothing. Peeking is **data leakage**, and its failure mode is the nastiest one available: a model that looks brilliant in the lab and fails disastrously in production, discovered only after deployment.

### Cross-validation

Cross-validation is not an alternative to the split above; the test set stays in the vault regardless. It hardens the validation step. A single fixed validation set can flatter a model that happened to get easy questions. Instead, the training data divides into K blocks (say 5), the model trains and evaluates 5 times rotating which block plays validator, and the winner is chosen on the mean across all folds. Five different exams on five different topics: a model with a high average across all of them is solid, not lucky. Only then does the winner face the test set.

## Phase 2: validation and evaluation

Final performance is measured on the test set to confirm the model generalises instead of having memorised. There is no universal report card; the metric follows the task:

- **Classification**: accuracy, precision, recall, F1-score.
- **Regression**: mean error, RMSE, MAE (an error in euros is an error stakeholders understand).
- **Unsupervised**: separation metrics such as silhouette score, and often qualitative human judgment, because there is no ground-truth answer. An expert looking at customer segments and saying "yes, these make commercial sense" is frequently the only real validation.
- **Vision / NLP**: task-specific metrics, IoU for object detection, BLEU for translation.

The unsupervised case deserves the architectural footnote: when validation is partly human, the review step has to exist in the process design, with an owner and a cadence, or it silently never happens.

### The enemy: overfitting

> Overfitting: the model learns the training data by heart, noise included, and loses the ability to capture the general pattern.

The student analogy from the deck holds up. A memorising student aces any question copied verbatim from the textbook and goes blank on a slightly reworded one. The diagnostic signature is the gap: around 99% accuracy on the training set collapsing to around 60% on validation or test. The model did not learn the concept, it memorised the examples. Everything in phase 1, the vaulted test set, the validation set, cross-validation, exists to surface this gap before production does.

## Phase 3: deployment

> Deployment is the process of integrating the model (the `.pkl` file) into the existing IT infrastructure so that end users or other systems can reach it.

A model that is trained, validated, and living on a laptop is technically working and commercially worthless. Deployment is the move from the safe data-science lab to the production jungle: the model has to talk to the website, the mobile app, the corporate database. Serving mechanics (FastAPI, Docker, CI/CD) are covered in depth in module 06 notes, and exercise 02 builds exactly this, a containerized FastAPI image classifier; what belongs here is the two decisions that precede the mechanics.

### First decision: optimize the artifact

Production brings constraints the lab never had: limited memory, modest CPUs, latency budgets. Three techniques put the model on a diet:

- **Pruning**: cut the weak or useless neural connections, like dead branches off a tree. The network gets sparser and lighter with little precision loss.
- **Quantization**: reduce numeric precision, for example float32 to int8. Roughly 4x less memory and faster arithmetic, because most of those decimal digits were not earning their keep.
- **Compilation and standardization**: export to a standard format such as **ONNX**, which decouples the model from Python and lets it run efficiently on whatever hardware production offers.

These are not exotic tricks for edge devices only (though note 08 shows they become mandatory there); on a real-time API they are often the difference between meeting the latency SLA and not.

### Second decision: batch or real-time

**Batch** is not "the nightly job", the defining trait is efficiency, not the clock. Nobody is waiting on screen, so the goal is maximum throughput at minimum cost: take a million records, split them into blocks, run tens or hundreds of processors in parallel, exploit idle hours or cheap spot instances, run the hardware at 100% and switch it off. Execution is decoupled from the user request.

**Real-time** puts the model in the front line. The card-swipe example is the cleanest: nobody waits until tomorrow to know if a transaction is approved. The model lives inside an always-on web server (REST or gRPC), receives one request, computes inference on the fly, answers in milliseconds. It is technically the more stressful pattern on two axes: **scalability** (100,000 users arriving at once must not melt the service) and **high availability** (there is no "off", uptime is an SLA). This is also where the optimization work stops being optional, since a heavy model translates directly into user-visible wait.

The pattern choice is an architecture-level decision, not a serving detail: it drives cost structure, infrastructure shape, and failure modes, and it maps onto the batch vs streaming discussion of note 02. Scaling and resilience for the real-time path get their own treatment in note 09.

## Phase 4: monitoring

Deployment is not the end, because models age, and they age badly. The deck names the causes and the symptom:

- **Data drift**: the statistics of the input data shift away from the training distribution. A model trained on summer purchasing habits and used in winter sees data it never learned.
- **Concept drift**: the sneakier one. Inputs look the same, but their meaning has flipped. Someone buying 100 surgical masks in 2018 read as "doctor"; in 2020 the same purchase read as "worried citizen". The model did not change, the data barely changed, the underlying concept inverted.
- **Model drift**: the measured performance decay (accuracy, F1 trending down). It is the symptom of the causes above, and the signal to act.

### Retraining: closing the loop

The cure for an aged model is not manual patching, it is regeneration. Monitoring systems act as sentries with two trigger families:

- **Performance-based**: a key metric drops below a preset critical threshold.
- **Data-based**: the input distribution diverges significantly from the training one.

In a mature setup the alarm does not wake a human at night, it wakes the automated pipeline:

```
  production traffic --> monitor (metrics + input statistics)
                              |
                        drift detected
                              v
        pull fresh data --> retrain --> validate v2
                                           |
                          v2 beats v1? --> yes --> swap in production
```

The system pulls recent data, retrains from scratch, validates the candidate, and promotes it only if it beats the incumbent. This is the actual objective of MLOps: a system that self-corrects and adapts to change. The catch, and it is a real one: "automatic" retraining is only as safe as its validation gate. An automated swap with a weak gate industrialises the deployment of bad models, so the gate deserves the same design attention as the trigger. The data-based trigger is the more architecturally interesting of the two, because it fires before business damage shows up in the metrics; the performance trigger, by definition, fires after. Monitoring infrastructure and the deployment strategies that make swaps safe are covered in depth in module 06 notes (note 09 there).

The deck closes on the question that opens the next lesson: must every model be grown from a blank page? No. Pretrained models and the model registry, note 06, are how you stand on the shoulders of giants and manage the artifacts this lifecycle produces.

## Gotchas

- **Treating the ML pipeline as ETL with extra steps.** Different contract: ETL guarantees consistency, ML delivers an estimate. Monitoring is what a probabilistic artifact demands and a deterministic one does not.
- **Using the test set to make decisions.** That is data leakage, and it manufactures lab-only geniuses. The test set is opened once, for the final grade, and never before.
- **Reading cross-validation as a replacement for the test set.** It rotates inside the training data to make model selection robust; the vaulted test set stays untouched either way.
- **Celebrating training accuracy.** 99% on training data is not a result, it is a symptom candidate. The number that matters is the gap between training and test performance.
- **Choosing batch by the clock instead of by the user.** Batch is about nobody waiting, parallel throughput, and cheap compute, not about running at 3am. If a user is watching a spinner, it is real-time, with everything that implies for SLA and scaling.
- **Shipping the lab artifact as-is.** Pruning, quantization, and ONNX export exist because production hardware and latency budgets are not the data scientist's workstation. Optimization is part of deployment, not an afterthought.
- **Designing the architecture as a line.** No inference-time data capture, no retraining path, no swap mechanism means the first drift episode turns into a manual emergency project. The loop is drawn into the architecture on day one or retrofitted at ten times the cost.

## See also

- Note 02 (architectural patterns): batch vs streaming as general patterns; the deployment patterns here are their inference-time instances
- Note 04 (big data and data foundations): the ETL side that feeds this pipeline
- Note 06 (pretrained vs custom models and model registry): when not to train from scratch, and where the artifacts of this lifecycle live
- Note 08 (edge AI vs cloud AI): where pruning and quantization stop being optimizations and become entry requirements
- Note 09 (scalability, resilience, testing): the real-time serving challenges, scalability and high availability, in depth
- Module 06 notes: MLOps foundations, CI/CD, serving with FastAPI, Docker, and production monitoring, the engineering implementation of this loop
- Exercise 01 (data pipeline with Python) for the ETL half; exercise 02 (API and enterprise integration) for the real-time deployment half
